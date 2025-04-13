# How to Run the AI-Powered Astrology Consultation

This application uses ChatCerebras from LangChain for AI-powered astrological consultations and Tavily for web search capabilities. Follow these steps to set up and run the application.

## Prerequisites

- Python 3.8 or higher
- A valid Cerebras API key
- A valid Tavily API key (for web search capabilities)

## Setup

1. **Clone the repository** (or download the files)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   Edit the `.env` file in the root directory and add your API keys:
   ```
   SECRET_KEY=your_secret_key_here
   CEREBRAS_API_KEY=your_cerebras_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Running the Application

1. **Start the Flask server**:
   ```bash
   python run.py
   ```

2. **Access the web application**:
   Open your browser and visit:
   ```
   http://localhost:5000
   ```

## Using the Application

1. **Generate a natal chart**:
   - Enter your name, date of birth, time of birth, and location of birth
   - Click "Generate My Chart"

2. **View your natal chart**:
   - Explore your sun sign, moon sign, rising sign, and other planetary positions
   - See the visual representation of your chart

3. **Get an astrological consultation**:
   - Navigate to the Consultation page
   - Ask questions about your chart, future, relationships, career, etc.
   - The AI will analyze your chart and provide personalized insights
   - The application uses Tavily to search for relevant astrological information based on your chart and question

## Troubleshooting

- If you encounter issues with the Cerebras integration, verify that your API key is correct and that you have access to the models.
- If you see errors related to Tavily search, make sure your API key is valid and that you have sufficient search quota.
- If you see errors related to pyswisseph, make sure the library is installed correctly.
- For any other issues, check the console output for error messages.

## References

- [LangChain Cerebras Documentation](https://python.langchain.com/docs/integrations/chat/cerebras/)
- [LangChain Tavily Search Documentation](https://python.langchain.com/docs/integrations/tools/tavily_search/)
- [ChatCerebras API Reference](https://python.langchain.com/api_reference/cerebras/chat_models/langchain_cerebras.chat_models.ChatCerebras.html) 