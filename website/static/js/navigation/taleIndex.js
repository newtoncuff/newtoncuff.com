document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cards');
    const cardModal = document.getElementById('cardModal');
    const modalBody = cardModal.querySelector('.modal-body');
    const modalClose = cardModal.querySelector('.modal-close');
    
    // Insert close button before the close button
    cardModal.querySelector('.modal-content').append(modalClose);
    
    // Create error message element if it doesn't exist
    let errorMessage = document.getElementById('error-message');
    if (!errorMessage) {
        errorMessage = document.createElement('div');
        errorMessage.id = 'error-message';
        errorMessage.style.display = 'none';
        cardsContainer.parentNode.insertBefore(errorMessage, cardsContainer.nextSibling);
    }

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
        topicTitle: cardElement.querySelector('.topicTitle').textContent,
        date: cardElement.querySelector('.date').textContent,
        location: cardElement.querySelector('.location').textContent,
        talltale: cardElement.querySelector('.talltale').textContent,
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
            <h1>${card.topicTitle || 'Untitled'}</h1>
            <div class="card-separator" style="margin-bottom: 20px;"></div>
            
            <div style="margin-bottom: 15px;">
                <div style="margin-top: 5px;">${card.date}</div>
            </div>
        `;

        // Add location if it exists
        if (card.location) {
            modalContent += `
                <div style="margin-bottom: 15px;">
                    <div style="margin-top: 5px;">${card.location}</div>
                </div>
            `;
        }

        // Add talltale content if it exists
        if (card.talltale) {
            modalContent += `
                <div style="margin-bottom: 15px;">
                    <div style="margin-top: 5px;">${card.talltale}</div>
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