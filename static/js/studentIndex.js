// Global variables
let currentStep = 1;
let selectedDate = '';
let selectedTime = '';
let selectedCounselorId = '';
let selectedCounselorName = '';

// Document Ready Handler
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeMoodSelector();
    initializeNotifications();
    initializeSearch();
    setupEventListeners();
});

// Sidebar Functionality
function initializeSidebar() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('content').classList.toggle('active');
        });
    }
}

// Mood Selector
function initializeMoodSelector() {
    const moodButtons = document.querySelectorAll('.mood-btn');
    moodButtons.forEach(button => {
        button.addEventListener('click', function() {
            moodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            saveMoodSelection(this.textContent.trim());
        });
    });
}

function saveMoodSelection(mood) {
    // You can implement mood tracking here if needed
    console.log('Mood selected:', mood);
    showMessage(`Thank you for sharing how you're feeling!`, 'success');
}

// Notifications
function initializeNotifications() {
    const notificationDropdown = document.querySelector('.dropdown');
    if (notificationDropdown) {
        const badge = notificationDropdown.querySelector('.badge');
        const notifications = notificationDropdown.querySelectorAll('.dropdown-item');
        
        // Update badge count
        if (badge && notifications) {
            badge.textContent = notifications.length;
        }
    }
}

// Search Functionality
function initializeSearch() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="search"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                showMessage('Please enter a search term', 'warning');
            }
        });
    }
}

// Session Management
function bookSession(counselorId, counselorName) {
    selectedCounselorId = counselorId;
    selectedCounselorName = counselorName;
    resetBookingModal();
    new bootstrap.Modal(document.getElementById('bookingModal')).show();
}

function cancelSession(bookingId) {
    if (confirm('Are you sure you want to cancel this session?')) {
        fetch(`/cancel-booking/${bookingId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage('Session cancelled successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showMessage(data.message || 'Failed to cancel session', 'error');
            }
        })
        .catch(() => {
            showMessage('An error occurred. Please try again.', 'error');
        });
    }
}

function rescheduleSession(bookingId) {
    selectedBookingId = bookingId;
    new bootstrap.Modal(document.getElementById('rescheduleModal')).show();
}

// Utility Functions
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function setupEventListeners() {
    // Session action buttons
    document.querySelectorAll('.session-actions button').forEach(button => {
        if (button.textContent.includes('Cancel')) {
            button.addEventListener('click', function() {
                const bookingId = this.closest('.session-card').dataset.bookingId;
                cancelSession(bookingId);
            });
        } else if (button.textContent.includes('Reschedule')) {
            button.addEventListener('click', function() {
                const bookingId = this.closest('.session-card').dataset.bookingId;
                rescheduleSession(bookingId);
            });
        }
    });

    // Handle completed sessions for rating
    document.querySelectorAll('.session-card[data-status="completed"]').forEach(card => {
        if (!card.dataset.rated) {
            const rateButton = document.createElement('button');
            rateButton.className = 'btn btn-sm btn-outline-primary';
            rateButton.innerHTML = '<i class="fas fa-star"></i> Rate Session';
            rateButton.addEventListener('click', function() {
                const bookingId = card.dataset.bookingId;
                showRatingModal(bookingId);
            });
            card.querySelector('.session-actions').appendChild(rateButton);
        }
    });

    // Profile completion reminder
    // checkProfileCompletion();
}

// function checkProfileCompletion() {
    // const profile = {
    //     name: document.querySelector('.profile-name')?.textContent,
    //     email: document.querySelector('.profile-email')?.textContent,
    //     phone: document.querySelector('.profile-phone')?.textContent,
    //     // Add other profile fields
    // };

    // const incomplete = Object.entries(profile).filter(([key, value]) => !value).map(([key]) => key);
    // if (incomplete.length > 0) {
    //     showMessage(`Please complete your profile: ${incomplete.join(', ')}`, 'warning');
    // }
// }

// Export functions for use in other scripts
window.bookSession = bookSession;
window.cancelSession = cancelSession;
window.rescheduleSession = rescheduleSession;
window.showMessage = showMessage;