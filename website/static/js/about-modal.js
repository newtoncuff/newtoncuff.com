document.addEventListener('DOMContentLoaded', function() {
    // Get the modal elements
    const aboutLink = document.getElementById('about-me-link');
    const aboutModal = document.getElementById('about-modal');
    const modalClose = aboutModal.querySelector('.modal-close');
    
    // Open modal when clicking the About Me link
    aboutLink.addEventListener('click', function(e) {
        e.preventDefault();
        aboutModal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    });
    
    // Close modal when clicking X button
    modalClose.addEventListener('click', function() {
        aboutModal.style.display = 'none';
        document.body.style.overflow = ''; // Restore scrolling
    });
    
    // Close modal when clicking outside content area
    aboutModal.addEventListener('click', function(event) {
        if (event.target === aboutModal) {
            aboutModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && aboutModal.style.display === 'flex') {
            aboutModal.style.display = 'none';
            document.body.style.overflow = ''; // Restore scrolling
        }
    });
});