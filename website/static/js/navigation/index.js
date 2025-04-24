document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cards');
    const cardModal = document.getElementById('cardModal');
    const modalBody = cardModal.querySelector('.modal-body');
    const modalClose = cardModal.querySelector('.modal-close');
    
    // Create Add Tale button
    const modalAdd = document.createElement('span');
    modalAdd.classList.add('modal-add');
    modalAdd.innerHTML = '&#43;'; // + symbol
    modalAdd.setAttribute('title', 'Add a Tale for this item');
    
    // Insert Add button before the close button
    cardModal.querySelector('.modal-content').insertBefore(modalAdd, modalClose);
    
    // Create error message element if it doesn't exist
    let errorMessage = document.getElementById('error-message');
    if (!errorMessage) {
        errorMessage = document.createElement('div');
        errorMessage.id = 'error-message';
        errorMessage.style.display = 'none';
        cardsContainer.parentNode.insertBefore(errorMessage, cardsContainer.nextSibling);
    }
    
    // Add CSS for the add button
    const style = document.createElement('style');
    style.textContent = `
        .modal-add {
            position: absolute;
            top: 10px;
            left: 15px;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            color: #4CAF50;
        }
        
        .modal-add:hover {
            color: #388E3C;
        }
        
        .tale-form {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        
        .tale-form h2 {
            margin-bottom: 15px;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input[type="text"],
        .form-group input[type="datetime-local"],
        .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        
        .form-group textarea {
            height: 150px;
            resize: vertical;
        }
        
        .submit-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .submit-btn:hover {
            background-color: #388E3C;
        }
        
        .modal-content.expanded {
            height: auto;
            max-height: 90vh;
        }
    `;
    document.head.appendChild(style);
    
    // Helper function to format date for datetime-local input
    function formatDateForInput(date) {
        if (!date) date = new Date();
        return date.toISOString().slice(0, 16); // format as YYYY-MM-DDTHH:MM
    }
    
    // Add Tale form creation function
    function showTaleForm(cardData) {
        // Expand the modal
        cardModal.querySelector('.modal-content').classList.add('expanded');
        
        // Create form HTML
        const formHTML = `
            <div class="tale-form">
                <h2>Add a Tale for "${cardData.title}"</h2>
                <form id="add-tale-form">
                    <input type="hidden" name="mindObjectType" value="${objectType || ''}">
                    <input type="hidden" name="mindObjectTypeId" value="${cardData.id || ''}">
                    <input type="hidden" name="topicTitle" value="${cardData.title || ''}">
                    
                    <div class="form-group">
                        <label for="date">Date:</label>
                        <input type="datetime-local" id="date" name="date" value="${formatDateForInput()}" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="location">Location:</label>
                        <input type="text" id="location" name="location" placeholder="Where did this happen?">
                    </div>
                    
                    <div class="form-group">
                        <label for="talltale">Your Tale:</label>
                        <textarea id="talltale" name="talltale" placeholder="Tell your tale here..." required></textarea>
                    </div>
                    <button type="submit" class="submit-btn">Save Tale</button>
                </form>
            </div>
        `;
        
        // Append form to modal body
        modalBody.innerHTML += formHTML;
        
        // Setup form submission
        document.getElementById('add-tale-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitBtn = this.querySelector('.submit-btn');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Saving...';
            submitBtn.disabled = true;
            
            // Collect form data
            const formData = new FormData(this);
            
            // Convert FormData to JSON
            const taleData = {};
            formData.forEach((value, key) => {
                taleData[key] = value;
            });
            
            // Get the current path for the API endpoint
            const pathParts = window.location.pathname.split('/');
            const objectType = pathParts[1] || ''; // e.g., 'passions', 'thoughts', etc.

            // Make sure mindObjectType in the data matches the URL path
            taleData.mindObjectType = objectType;

            // Log what we're sending
            console.log(`Submitting tale for ${objectType}:`, taleData);
            
            // Make the API call - use relative URL that works with current page path
            fetch('addTale', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taleData)
            })
            .then(response => {
                // Check if response is OK
                if (!response.ok) {
                    return response.json().then(errorData => {
                        throw new Error(errorData.error || `Server error: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                
                // Show success message
                alert('Tale added successfully!');
                
                // Close the modal
                const cardModal = document.getElementById('cardModal');
                cardModal.style.display = 'none';
                document.body.style.overflow = ''; // Restore scrolling
                
                // Optional: Update UI to show the new tale was added
                // For example, add a small indicator to the card
                const cardId = taleData.mindObjectTypeId;
                const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);
                if (cardElement) {
                    // Add a "new tale" indicator if it doesn't exist
                    if (!cardElement.querySelector('.tale-indicator')) {
                        const indicator = document.createElement('div');
                        indicator.className = 'tale-indicator';
                        indicator.title = 'Has tales';
                        indicator.innerHTML = '📖';
                        indicator.style.position = 'absolute';
                        indicator.style.top = '5px';
                        indicator.style.right = '5px';
                        indicator.style.fontSize = '16px';
                        cardElement.style.position = 'relative';
                        cardElement.appendChild(indicator);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Show error message
                const errorMsg = error.message || 'Failed to add tale';
                alert(`Error: ${errorMsg}`);
            })
            .finally(() => {
                // Reset button state
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
            });
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
    
    // Show Tale form when clicking + button
    modalAdd.addEventListener('click', function() {
        // Get current card data from modal
        const title = modalBody.querySelector('h1').textContent;
        const currentId = cardModal.getAttribute('data-current-id');
        
        showTaleForm({
            id: currentId,
            title: title
        });
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
    
    setupCardInteractions();
});

// Helper function to find a card by ID from pre-rendered data
function findCardById(id) {
    // Find the card element with the matching ID
    const cardElement = document.querySelector(`.card[data-id="${id}"]`);
    
    if (!cardElement) return null;
    
    // Extract data from the card element
    return {
        id: id,
        title: cardElement.querySelector('h3').textContent,
        content: cardElement.querySelector('p').textContent,
        subtopic: cardElement.querySelector('.subtopic') ? 
                 cardElement.querySelector('.subtopic').textContent : null,
        tag: cardElement.querySelector('.tag') ? 
             cardElement.querySelector('.tag').textContent : null
    };
}

// Update showCardModal function to store the current card ID
function showCardModal(id) {
    const card = findCardById(id);
    
    if (card) {
        const cardModal = document.getElementById('cardModal');
        const modalBody = cardModal.querySelector('.modal-body');
        
        // Store the current card ID as a data attribute on the modal
        cardModal.setAttribute('data-current-id', id);
        
        // Get the current object type from URL
        const pathParts = window.location.pathname.split('/');
        window.objectType = pathParts[1]; // e.g., 'thoughts', 'passions', etc.
        
        // Create modal content
        let modalContent = `
            <h1>${card.title || 'Untitled'}</h1>
            <div class="card-separator" style="margin-bottom: 20px;"></div>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: #555; font-size: 1.1em;">Content:</strong>
                <div style="margin-top: 5px;">${card.content}</div>
            </div>
        `;
        
        // Add subtopic if it exists
        if (card.subtopic) {
            modalContent += `
                <div style="margin-bottom: 15px;">
                    <strong style="color: #555; font-size: 1.1em;">Subtopic:</strong>
                    <div style="margin-top: 5px;">${card.subtopic}</div>
                </div>
            `;
        }
        
        // Add tags if they exist
        if (card.tag) {
            modalContent += `
                <div style="margin-bottom: 15px;">
                    <strong style="color: #555; font-size: 1.1em;">Tags:</strong>
                    <div style="margin-top: 5px;">${card.tag}</div>
                </div>
            `;
        }
        
        modalBody.innerHTML = modalContent;
        
        // Reset modal height if previously expanded
        cardModal.querySelector('.modal-content').classList.remove('expanded');
        
        // Display the modal
        cardModal.style.display = 'flex';
        
        // Prevent scrolling of the background
        document.body.style.overflow = 'hidden';
    }
}

function setupCardInteractions() {
    // Handle card clicks to show modal
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', () => {
            // Show modal with card details
            showCardModal(card.dataset.id);
        });
    });
}