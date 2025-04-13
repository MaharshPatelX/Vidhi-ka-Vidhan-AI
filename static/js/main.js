document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const birthChartForm = document.getElementById('birth-chart-form');
    const chartContainer = document.getElementById('chart-container');
    const chartInfo = document.getElementById('chart-info');
    const consultationForm = document.getElementById('consultation-form');
    const chatHistory = document.getElementById('chat-history');
    const clearChatButton = document.getElementById('clear-chat-button');
    
    // Event listeners
    if (birthChartForm) {
        birthChartForm.addEventListener('submit', handleChartFormSubmit);
    }
    
    if (consultationForm) {
        consultationForm.addEventListener('submit', handleConsultationFormSubmit);
    }
    
    // Added listener for clear chat button
    if (clearChatButton) {
        clearChatButton.addEventListener('click', handleClearChatClick);
    }
    
    // Check for previously generated chart
    checkPreviousSession();
    
    // Load previous consultation messages if on consultation page
    if (chatHistory) {
        loadPreviousMessages();
    }
});

// Handle birth chart form submission
async function handleChartFormSubmit(event) {
    event.preventDefault();
    
    // Show loading state
    const submitButton = this.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.textContent = 'Generating...';
    submitButton.disabled = true;
    
    // Get form data
    const formData = new FormData(this);
    const chartData = {
        name: formData.get('name'),
        birthDate: formData.get('birth-date'),
        birthTime: formData.get('birth-time'),
        birthLocation: formData.get('birth-location')
    };
    
    try {
        // Send API request
        const response = await fetch('/api/generate-chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(chartData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save data to session storage
            sessionStorage.setItem('chartData', JSON.stringify(data.chart_data));
            sessionStorage.setItem('userProfile', JSON.stringify(chartData));
            
            // Display chart
            displayChart(data.chart_data);
            
            // Redirect to chart page if not already there
            if (window.location.pathname !== '/natal-chart') {
                window.location.href = '/natal-chart';
            }
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error generating chart:', error);
        alert('An error occurred while generating your chart. Please try again.');
    } finally {
        // Restore button state
        submitButton.textContent = originalButtonText;
        submitButton.disabled = false;
    }
}

// Display the generated chart
function displayChart(chartData) {
    const chartContainer = document.getElementById('chart-container');
    const chartInfo = document.getElementById('chart-info');
    
    if (!chartContainer || !chartInfo) return;
    
    // Show chart container
    chartContainer.style.display = 'block';
    
    // Get user profile from session storage
    const userProfile = JSON.parse(sessionStorage.getItem('userProfile'));
    
    // Format chart display
    const sunSign = chartData.planets.Sun.sign;
    const moonSign = chartData.planets.Moon.sign;
    const ascendant = chartData.ascendant.sign;
    
    // Create chart SVG (simplified for this example)
    // In a real app, this would use D3.js or another library to draw a proper astrological chart
    const svgContent = createChartSVG(chartData);
    chartContainer.innerHTML = svgContent;
    
    // Display chart information
    chartInfo.innerHTML = `
        <h2>${userProfile.name}'s Natal Chart</h2>
        <div class="info-text">
            <p><strong>Birth Date:</strong> ${userProfile.birthDate}</p>
            <p><strong>Birth Time:</strong> ${userProfile.birthTime}</p>
            <p><strong>Birth Location:</strong> ${userProfile.birthLocation}</p>
            <p><strong>Sun Sign:</strong> ${sunSign}</p>
            <p><strong>Moon Sign:</strong> ${moonSign}</p>
            <p><strong>Ascendant:</strong> ${ascendant}</p>
        </div>
        <h3>Planetary Positions</h3>
        <div class="info-text">
            ${formatPlanetaryPositions(chartData.planets)}
        </div>
    `;
    
    // Add disclaimer below the chart info
    const disclaimer = document.createElement('p');
    disclaimer.style.textAlign = 'center';
    disclaimer.style.fontSize = '0.9em';
    disclaimer.style.marginTop = '15px';
    disclaimer.style.color = '#aaa';
    disclaimer.textContent = 'Note: This chart visualizes randomly generated data for illustrative purposes and is not astronomically accurate.';
    chartInfo.appendChild(disclaimer);
}

// Create SVG representation of the chart
function createChartSVG(chartData) {
    // This is a simplified placeholder
    // In a real app, this would generate an actual astrological chart wheel
    return `
        <svg class="chart-wheel" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
            <!-- Chart background circle -->
            <circle cx="250" cy="250" r="240" fill="#0e0e0e" stroke="#333" stroke-width="1" />
            
            <!-- Zodiac wheel -->
            <circle cx="250" cy="250" r="220" fill="none" stroke="#333" stroke-width="1" />
            <circle cx="250" cy="250" r="180" fill="none" stroke="#333" stroke-width="0.5" /> // Inner ring for houses
            
            <!-- House dividers -->
            ${createHouseDividers(chartData.houses.cusps, chartData.ascendant.position, chartData.midheaven.position)}
            
            <!-- House Numbers -->
            ${createHouseNumbers(chartData.houses.cusps)}
            
            <!-- Zodiac signs markers -->
            ${createZodiacMarkers()}
            
            <!-- Planet positions -->
            ${createPlanetMarkers(chartData.planets, chartData.ascendant.position)}
            
            <!-- Center point -->
            <circle cx="250" cy="250" r="5" fill="#fff" />
        </svg>
    `;
}

// Create house divider lines
function createHouseDividers(cusps, ascDegree, mcDegree) {
    let dividers = '';
    const center = 250;
    const outerRadius = 220;
    const innerRadius = 50; // Extend lines closer to center

    // Ensure cusps is an array of 12 numbers
    if (!Array.isArray(cusps) || cusps.length !== 12) {
        console.error('Invalid cusps data for drawing dividers');
        // Draw default radial lines if cusps are invalid
        for (let i = 0; i < 12; i++) {
            const angleRad = (i * 30) * Math.PI / 180;
            const x1 = center + Math.cos(angleRad) * outerRadius;
            const y1 = center + Math.sin(angleRad) * outerRadius;
            const x2 = center + Math.cos(angleRad) * innerRadius;
            const y2 = center + Math.sin(angleRad) * innerRadius;
            dividers += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#444" stroke-width="0.5" />`;
        }
        return dividers;
    }

    for (let i = 0; i < 12; i++) {
        const cuspDegree = cusps[i];
        // Orient chart with 0 Aries at the left (standard astrological practice)
        // Subtracting 90 degrees rotates the coordinate system
        const angleRad = (cuspDegree - 90) * Math.PI / 180;
        
        const x1 = center + Math.cos(angleRad) * outerRadius;
        const y1 = center + Math.sin(angleRad) * outerRadius;
        const x2 = center + Math.cos(angleRad) * innerRadius;
        const y2 = center + Math.sin(angleRad) * innerRadius;
        
        let stroke = "#444";
        let strokeWidth = 0.5;
        
        // Highlight Ascendant (cusp 0) and Midheaven (cusp 9)
        if (i === 0 || i === 9) { 
            stroke = "#aaa";
            strokeWidth = 1.5;
        }
        
        dividers += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="${strokeWidth}" />`;
        
        // Add AC/MC labels
        if (i === 0) { // Ascendant
             const labelX = center + Math.cos(angleRad) * (innerRadius - 15); // Place outside inner radius
             const labelY = center + Math.sin(angleRad) * (innerRadius - 15);
             dividers += `<text x="${labelX}" y="${labelY}" fill="#aaa" font-size="10" text-anchor="middle" dominant-baseline="middle">AC</text>`;
        } else if (i === 9) { // Midheaven
             const labelX = center + Math.cos(angleRad) * (innerRadius - 15);
             const labelY = center + Math.sin(angleRad) * (innerRadius - 15);
             dividers += `<text x="${labelX}" y="${labelY}" fill="#aaa" font-size="10" text-anchor="middle" dominant-baseline="middle">MC</text>`;
        }
    }
    
    return dividers;
}

// Create House Number Labels
function createHouseNumbers(cusps) {
    let numbers = '';
    const center = 250;
    const radius = 165; // Place numbers inside the inner house ring

    // Ensure cusps is an array of 12 numbers
    if (!Array.isArray(cusps) || cusps.length !== 12) {
        console.error('Invalid cusps data for drawing house numbers');
        return ''; // Return empty string if data is invalid
    }

    for (let i = 0; i < 12; i++) {
        const currentCusp = cusps[i];
        const nextCusp = cusps[(i + 1) % 12];
        
        // Calculate midpoint angle between cusps
        let midAngleDeg = 0;
        // Handle wrap-around from Pisces to Aries
        if (nextCusp < currentCusp) {
            midAngleDeg = ((currentCusp + (nextCusp + 360)) / 2) % 360;
        } else {
            midAngleDeg = (currentCusp + nextCusp) / 2;
        }
        
        // Orient chart with 0 Aries at the left
        const angleRad = (midAngleDeg - 90) * Math.PI / 180;
        
        const x = center + Math.cos(angleRad) * radius;
        const y = center + Math.sin(angleRad) * radius;
        
        // House numbers are 1-12
        numbers += `<text x="${x}" y="${y}" fill="#666" font-size="10" text-anchor="middle" dominant-baseline="middle">${i + 1}</text>`;
    }
    
    return numbers;
}

// Create zodiac sign markers
function createZodiacMarkers() {
    const signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];
    let markers = '';
    const center = 250;
    const radius = 200; // Place signs between outer rings
    
    for (let i = 0; i < 12; i++) {
        // Center of each 30-degree sign segment, oriented with 0 Aries at left
        const angleRad = ((i * 30 + 15) - 90) * Math.PI / 180;
        const x = center + Math.cos(angleRad) * radius;
        const y = center + Math.sin(angleRad) * radius;
        
        markers += `<text x="${x}" y="${y}" fill="white" font-size="16" text-anchor="middle" dominant-baseline="middle">${signs[i]}</text>`;
    }
    
    return markers;
}

// Create planet markers
function createPlanetMarkers(planets, ascendantDegree) { // Use ascendant degree for orientation
    let markers = '';
    const planetSymbols = {
        'Sun': '☉',
        'Moon': '☽',
        'Mercury': '☿',
        'Venus': '♀',
        'Mars': '♂',
        'Jupiter': '♃',
        'Saturn': '♄',
        'Uranus': '♅',
        'Neptune': '♆',
        'Pluto': '♇',
        'North Node': '☊',
        'Chiron': '⚷' // Added Chiron symbol
    };
    const center = 250;
    const baseRadius = 130; // Base radius for placing planets inside houses
    const radiusStep = 15; // Step inwards for each planet
    let planetIndex = 0;

    for (const [planet, data] of Object.entries(planets)) {
        if (!planetSymbols[planet] || !data || typeof data.longitude !== 'number') continue;
        
        // Orient chart with 0 Aries at the left
        const angleRad = (data.longitude - 90) * Math.PI / 180;
        
        // Position planets spiraling slightly inwards
        const radius = baseRadius - (planetIndex * (radiusStep / Object.keys(planets).length)); 
        
        const x = center + Math.cos(angleRad) * radius;
        const y = center + Math.sin(angleRad) * radius;
        
        const symbolColor = data.is_retrograde ? '#f5a623' : 'white'; // Orange for retrograde

        markers += `
            <text x="${x}" y="${y}" fill="${symbolColor}" font-size="14" text-anchor="middle" dominant-baseline="middle" style="cursor: default;" title="${planet} ${data.sign} ${data.position_in_sign.toFixed(1)}°${data.is_retrograde ? ' (R)' : ''}">${planetSymbols[planet]}</text>
        `;
        
        planetIndex++;
    }
    
    return markers;
}

// Format planetary positions for display
function formatPlanetaryPositions(planets) {
    let html = '';
    
    for (const [planet, data] of Object.entries(planets)) {
        const retrograde = data.is_retrograde ? ' (R)' : '';
        html += `<p><strong>${planet}:</strong> ${data.sign} ${data.position_in_sign.toFixed(1)}°${retrograde}</p>`;
    }
    
    return html;
}

// Handle consultation form submission
async function handleConsultationFormSubmit(event) {
    event.preventDefault();
    
    const questionInput = document.getElementById('question');
    const question = questionInput.value.trim();
    
    if (!question) return;
    
    // Add user message to chat
    addMessageToChat('user', question);
    
    // Clear input
    questionInput.value = '';
    
    try {
        // Show loading indicator
        addMessageToChat('loading', 'The astrologer is analyzing your chart...');
        
        // Send question to server
        const response = await fetch('/api/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        // Remove loading message
        removeLoadingMessage();
        
        if (data.success) {
            // Add astrologer response to chat
            addMessageToChat('astrologer', data.response);
        } else {
            // Show error
            addMessageToChat('system', `Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error submitting question:', error);
        removeLoadingMessage();
        addMessageToChat('system', 'An error occurred while processing your question. Please try again.');
    }
}

// Add a message to the chat history
function addMessageToChat(type, content) {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    if (type === 'loading') {
        messageDiv.id = 'loading-message';
        messageDiv.innerHTML = `
            <p>${content}</p>
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `<p>${content}</p>`;
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Save to session storage if not a loading message
    if (type !== 'loading' && type !== 'system') {
        saveMessageToHistory(type, content);
    }
}

// Remove the loading message
function removeLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Save message to session storage
function saveMessageToHistory(type, content) {
    let history = JSON.parse(sessionStorage.getItem('chatHistory')) || [];
    history.push({ type, content, timestamp: new Date().toISOString() });
    sessionStorage.setItem('chatHistory', JSON.stringify(history));
}

// Load previous messages from session storage
function loadPreviousMessages() {
    const history = JSON.parse(sessionStorage.getItem('chatHistory')) || [];
    
    for (const message of history) {
        addMessageToChat(message.type, message.content);
    }
}

// Check for previous session data
function checkPreviousSession() {
    const chartData = sessionStorage.getItem('chartData');
    
    if (chartData && window.location.pathname === '/natal-chart') {
        // Display previously generated chart
        displayChart(JSON.parse(chartData));
    }
}

// Handle Clear Chat button click
async function handleClearChatClick() {
    // Optional: Confirm with the user
    if (!confirm("Are you sure you want to clear the chat history?")) {
        return;
    }

    try {
        const response = await fetch('/api/clear-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();

        if (data.success) {
            // Clear chat display
            const chatHistoryElement = document.getElementById('chat-history');
            if (chatHistoryElement) {
                // Keep the initial system message if desired, or clear completely
                chatHistoryElement.innerHTML = ''; // Clear all messages
                // Or to keep the welcome message:
                // chatHistoryElement.innerHTML = '<div class="message system-message"><p>Welcome! Ask me anything...</p></div>'; 
            }

            // Clear chat history from session storage
            sessionStorage.removeItem('chatHistory');
            console.log('Chat history cleared.');
            // Optionally add a message confirming clearance
            addMessageToChat('system', 'Chat history cleared.');

        } else {
            console.error('Error clearing chat:', data.error);
            alert('Failed to clear chat history: ' + data.error);
        }
    } catch (error) {
        console.error('Error during clear chat request:', error);
        alert('An error occurred while trying to clear the chat.');
    }
} 