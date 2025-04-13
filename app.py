from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import uuid
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import requests

# Import our custom modules
from astro_utils import calculate_natal_chart
from llm_utils import create_cerebras_llm, get_tavily_search

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "astro-consultation-secret")

# Initialize session storage for user data
user_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/natal-chart')
def natal_chart():
    return render_template('natal-chart.html')

@app.route('/consultation')
def consultation():
    return render_template('consultation.html')

@app.route('/api/generate-chart', methods=['POST'])
def generate_chart():
    try:
        data = request.json
        name = data.get('name')
        birth_date = data.get('birthDate')
        birth_time = data.get('birthTime')
        birth_location = data.get('birthLocation')
        
        # Generate a session ID for the user if not already present
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        
        user_id = session['user_id']
        
        # Calculate the natal chart using the astrological library
        chart_data = calculate_natal_chart(birth_date, birth_time, birth_location)
        
        # Store user data and chart info in the session storage
        # Always update the user's entry to handle server restarts during development
        user_sessions[user_id] = {
            "profile": {
                "name": name,
                "birth_date": birth_date,
                "birth_time": birth_time,
                "birth_location": birth_location
            },
            "chart_data": chart_data,
            # Preserve existing chat history and readings if the user is regenerating
            "chat_history": user_sessions.get(user_id, {}).get("chat_history", []),
            "readings": user_sessions.get(user_id, {}).get("readings", [])
        }
        
        return jsonify({
            "success": True,
            "chart_data": chart_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question')
        user_id = session.get('user_id')
        
        if not user_id or user_id not in user_sessions:
            return jsonify({
                "success": False,
                "error": "User session not found. Please generate your chart first."
            }), 400
        
        # Get user's profile and chart data
        user_data = user_sessions[user_id]
        profile = user_data["profile"]
        chart_data = user_data["chart_data"]
        
        # Perform web search for relevant astrological information
        search_results = get_tavily_search(question, profile, chart_data)
        
        # Create LLM instance
        llm = create_cerebras_llm()
        
        # Create a chat history from previous interactions
        chat_history = user_data.get("chat_history", [])
        
        # 1. Format the system message string FIRST
        system_message_content = f"""
        You are Vidhi ka Vidhan AI, an expert astrologer providing a consultation. 
        Your tone is encouraging and insightful. 
        Keep your responses CONCISE, CLEAR, and EASY TO UNDERSTAND. 
        Use relevant EMOJIS ✨ to make the response engaging. 
        Use BULLET POINTS for lists or key insights.
        Focus DIRECTLY on answering the user's specific question based on their chart and the provided context.
        Acknowledge the chart is generated if needed for context, but don't over-explain.

        User Profile:
        - Name: {profile.get('name', 'N/A')}
        - Birth Date: {profile.get('birth_date', 'N/A')}
        - Birth Time: {profile.get('birth_time', 'N/A')}
        - Birth Location: {profile.get('birth_location', 'N/A')}
        
        Natal Chart Information (Generated):
        {json.dumps(chart_data, indent=2)}
        
        Relevant Astrological Information from Research:
        {search_results}
        
        Now, answer the user's question concisely and clearly, using emojis and formatting.
        """

        # 2. Format chat history into LangChain message objects
        formatted_chat_history = []
        for message in chat_history:
            if message.get("role") == "user":
                formatted_chat_history.append(HumanMessage(content=message.get("content", "")))
            elif message.get("role") == "assistant":
                formatted_chat_history.append(AIMessage(content=message.get("content", "")))

        # --- Create Template and Chain --- 
        # 3. Create a ChatPromptTemplate using standard placeholders
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"), # Placeholder for the formatted system message
            MessagesPlaceholder(variable_name="chat_history"), # Placeholder for history list
            ("human", "{question}") # Placeholder for the current question
        ])
        
        # 4. Generate the response using the prompt, LLM, and providing ALL input variables
        chain = prompt | llm
        # Pass the actual variables to invoke
        response = chain.invoke({
            "system_message": system_message_content,
            "chat_history": formatted_chat_history, # Pass the list of message objects
            "question": question
        })
        
        # Extract content from AIMessage
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Add to chat history
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": response_text})
        user_data["chat_history"] = chat_history
        
        # Save this reading to the user's history
        reading = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "response": response_text
        }
        user_data["readings"].append(reading)
        
        return jsonify({
            "success": True,
            "response": response_text
        })
    
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/get-readings', methods=['GET'])
def get_readings():
    user_id = session.get('user_id')
    
    if not user_id or user_id not in user_sessions:
        return jsonify({
            "success": False,
            "error": "User session not found"
        }), 400
    
    readings = user_sessions[user_id]["readings"]
    
    return jsonify({
        "success": True,
        "readings": readings
    })

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    user_id = session.get('user_id')
    
    if not user_id or user_id not in user_sessions:
        return jsonify({
            "success": False,
            "error": "User session not found"
        }), 400
    
    try:
        # Clear the chat history for this user
        user_sessions[user_id]["chat_history"] = []
        print(f"Chat history cleared for user {user_id}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error clearing chat history for user {user_id}: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to clear chat history: {e}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 