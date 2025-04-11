document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cards');
    const cardModal = document.getElementById('cardModal');
    const modalBody = cardModal.querySelector('.modal-body');
    const modalClose = cardModal.querySelector('.modal-close');
    
    // Create error message element if it doesn't exist
    let errorMessage = document.getElementById('error-message');
    if (!errorMessage) {
        errorMessage = document.createElement('div');
        errorMessage.id = 'error-message';
        errorMessage.style.display = 'none';
        cardsContainer.parentNode.insertBefore(errorMessage, cardsContainer.nextSibling);
    }
    
    // Add loading indicator to card container
    cardsContainer.innerHTML = `
    <div style="text-align: center; padding: 40px; width: 100%;">
        <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                    border-radius: 50%; border-top: 4px solid #3498db; animation: spin 1s linear infinite;"></div>
        <p style="margin-top: 20px; color: #666;">Loading delusions...</p>
    </div>
    `;
    
    // Add animation style
// Find the modal-content style section in your CSS and update it
const style = document.createElement('style');
style.textContent = `
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;
    document.head.appendChild(style);
    
    // Function to load all cards at once
    function loadAllCards() {
        // Get the object type from the URL
        const pathParts = window.location.pathname.split('/');
        const objectType = pathParts[1]; // e.g., 'thoughts', 'passions', etc.
        
        // Construct URL for data fetch
        const url = `/${objectType}/data`;
        
        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(cards => {
                console.log('Received data:', cards);
                
                // Validate that we received an array
                if (!Array.isArray(cards)) {
                    throw new Error(`Invalid response format. Expected array but got: ${typeof cards}`);
                }
                
                // Clear loading indicator
                cardsContainer.innerHTML = '';
                
                if (cards.length === 0) {
                    cardsContainer.innerHTML = `
                    <div style="text-align: center; padding: 40px; width: 100%;">
                        <p style="color: #666;">No delusions found. Check back later for more content.</p>
                    </div>
                    `;
                    return;
                }
                
                // Create cards from the data
                cards.forEach(card => {
                    // Basic validation
                    if (!card || typeof card !== 'object') {
                        console.warn('Invalid card data:', card);
                        return;
                    }
                    
                    const cardElement = document.createElement('div');
                    cardElement.className = 'card';
                    
                    // Get properties with fallbacks
                    const title = card.title || 'Untitled';
                    const content = card.content || 'No description available';
                    
                    // Build card HTML
                    let cardHTML = `
                    <h1>${title}</h1>
                    <div class="card-separator"></div>
                    <h2>${content}</h2>
                    `;
                    
                    // Add subtopic if it exists
                    if (card.subtopic) {
                        cardHTML += `
                            <div style="margin-top: 10px; font-size: 0.9em;">
                            <strong>${card.subtopic}</strong>
                            <p>${card.subtopicDesc || ''}</p>
                            </div>
                        `;
                    }
                    
                    // Add tags if they exist
                    if (card.tag) {
                        cardHTML += `
                            <div style="margin-top: 10px; font-size: 0.8em; color: #666;">
                            ${card.tag.split(',').map(tag => `#${tag.trim()}`).join(' ')}
                            </div>
                        `;
                    }
                    
                    cardElement.innerHTML = cardHTML;
                    
                    // Add click handler to open modal
                    cardElement.addEventListener('click', function() {
                        console.log(`Card clicked: ${card.id}`);
                        openModal(card);
                    });
                    
                    cardsContainer.appendChild(cardElement);
                });
            })
            .catch(error => {
                console.error('Error fetching delusions:', error);
                
                // Show error message
                cardsContainer.innerHTML = `
                    <div style="text-align: center; padding: 20px; margin: 20px; background: #fff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h3 style="color: #d9534f;">Error loading delusions</h3>
                    <p style="color: #666;">Please try again later or contact support.</p>
                    <div style="margin-top: 15px; font-family: monospace; text-align: left; background: #f8f8f8; padding: 10px; border-radius: 3px; font-size: 12px; color: #666; white-space: pre-wrap; word-break: break-all;">
                        ${error.message}
                    </div>
                    <button onclick="location.reload()" style="margin-top: 15px; padding: 8px 16px; background: #5bc0de; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Retry
                    </button>
                    </div>
                `;
            });
    }
    
    // Function to open modal with card details
    function openModal(card) {
        // Populate modal content
        let modalContent = `
            <h1>${card.title || 'Untitled'}</h1>
            <div class="card-separator" style="margin-bottom: 20px;"></div>
        `;
        
        // Add all card properties to the modal
        for (const [key, value] of Object.entries(card)) {
            // Skip certain fields or null/undefined values
            if (key === 'id' || value === null || value === undefined) continue;
            
            // Format the property name (convert snake_case to Title Case)
            const formattedKey = key
                .replace(/_/g, ' ')
                .replace(/\w\S*/g, txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
            
            // Format the value based on its type
            let formattedValue = value;
            
            // Handle special cases
            if (key === 'tag' && typeof value === 'string') {
                formattedValue = value.split(',').map(tag => `#${tag.trim()}`).join(' ');
            } else if (typeof value === 'boolean') {
                formattedValue = value ? 'Yes' : 'No';
            } else if (typeof value === 'object') {
                formattedValue = JSON.stringify(value);
            }
            
            modalContent += `
                <div style="margin-bottom: 15px;">
                    <strong style="color: #555; font-size: 1.1em;">${formattedKey}:</strong>
                    <div style="margin-top: 5px;">${formattedValue}</div>
                </div>
            `;
        }
        
        modalBody.innerHTML = modalContent;
        
        // Display the modal
        cardModal.style.display = 'flex';
        
        // Prevent scrolling of the background
        document.body.style.overflow = 'hidden';
    }
    
    // Event listeners for modal
    
    // Close modal when clicking X button
    modalClose.addEventListener('click', function() {
        cardModal.style.display = 'none';
        document.body.style.overflow = ''; // Restore scrolling
    });
    
    // Close modal when clicking outside content area
    cardModal.addEventListener('click', function(event) {
        if (event.target === cardModal) {
            cardModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && cardModal.style.display === 'flex') {
            cardModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    });
    
    // Load all cards immediately
    loadAllCards();
});