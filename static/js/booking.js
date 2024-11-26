let currentStep = 1;
let selectedDate = '';
let selectedTime = '';
let selectedCounselorId = '';
let selectedCounselorName = '';

// Initialize when document is ready
// document.addEventListener('DOMContentLoaded', function() {
//     initializeDatePicker();
//     initializeBookingButtons();
//     initializeNavigationButtons();
//     initializeSidebar();
//     initializeMoodSelector();
//     initializeSettingsModal();
// });

// Update the document ready function
document.addEventListener('DOMContentLoaded', function() {
    initializeDatePicker();
    initializeBookingButtons();
    initializeNavigationButtons();
    initializeSidebar();
    initializeMoodSelector();
    initializeSettingsModal();
    initializeProfileSettings(); // Add this line
});

// Add this new function
function initializeProfileSettings() {
    const settingsLink = document.getElementById('settingsLink');
    if (settingsLink) {
        settingsLink.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
            modal.show();
        });
    }
}

// Initialize date picker constraints
function initializeDatePicker() {
    const today = new Date();
    const nextMonth = new Date(today);
    nextMonth.setMonth(today.getMonth() + 1);

    const datePicker = document.getElementById('bookingDate');
    if (datePicker) {
        datePicker.min = today.toISOString().split('T')[0];
        datePicker.max = nextMonth.toISOString().split('T')[0];
        datePicker.addEventListener('change', handleDateSelection);
    }
}

// Initialize booking buttons
function initializeBookingButtons() {
    document.querySelectorAll('.btn-book').forEach(button => {
        button.addEventListener('click', function() {
            selectedCounselorId = this.dataset.counselorId;
            selectedCounselorName = this.dataset.counselorName;
            resetBookingModal();
            new bootstrap.Modal(document.getElementById('bookingModal')).show();
        });
    });
}

// Initialize navigation buttons
function initializeNavigationButtons() {
    const nextStepBtn = document.getElementById('nextStep');
    const confirmBookingBtn = document.getElementById('confirmBooking');

    if (nextStepBtn) {
        nextStepBtn.addEventListener('click', handleNextStep);
    }

    if (confirmBookingBtn) {
        confirmBookingBtn.addEventListener('click', handleBookingConfirmation);
    }
}

// Handle date selection
function handleDateSelection(event) {
    selectedDate = event.target.value;
    if (selectedDate) {
        fetchAvailableSlots();
    }
}

// Fetch available slots from server
async function fetchAvailableSlots() {
    try {
        const response = await fetch(`/get-counselor-slots/${selectedCounselorId}?date=${selectedDate}`);
        const data = await response.json();
        
        if (response.ok) {
            displayTimeSlots(data.slots);
        } else {
            showErrorMessage(data.message || 'Error fetching available slots');
        }
    } catch (error) {
        showErrorMessage('Network error occurred. Please try again.');
    }
}

// Display time slots
function displayTimeSlots(slots) {
    const slotsContainer = document.querySelector('.time-slots');
    slotsContainer.innerHTML = '';
    
    if (slots.length === 0) {
        slotsContainer.innerHTML = '<p class="text-muted">No available slots for this date</p>';
        return;
    }

    slots.forEach(slot => {
        const button = document.createElement('button');
        button.className = 'btn btn-outline-primary m-1 time-slot-btn';
        button.textContent = slot;
        button.onclick = () => selectTimeSlot(slot);
        slotsContainer.appendChild(button);
    });
}

// Handle time slot selection
function selectTimeSlot(time) {
    selectedTime = time;
    document.querySelectorAll('.time-slot-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent === time) {
            btn.classList.add('active');
        }
    });
}

// Handle next step in booking process
function handleNextStep() {
    if (currentStep === 1 && selectedDate) {
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        currentStep = 2;
    } else if (currentStep === 2 && selectedTime) {
        document.getElementById('step2').style.display = 'none';
        document.getElementById('step3').style.display = 'block';
        document.getElementById('nextStep').style.display = 'none';
        document.getElementById('confirmBooking').style.display = 'block';
        updateBookingSummary();
        currentStep = 3;
    } else {
        showErrorMessage('Please make a selection before proceeding');
    }
}

// Update booking summary
function updateBookingSummary() {
    document.getElementById('summaryName').textContent = selectedCounselorName;
    document.getElementById('summaryDate').textContent = formatDate(selectedDate);
    document.getElementById('summaryTime').textContent = selectedTime;
}

// Handle booking confirmation
async function handleBookingConfirmation() {
    const formData = new FormData();
    formData.append('counselor_id', selectedCounselorId);
    formData.append('date', selectedDate);
    formData.append('time', selectedTime);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    try {
        const response = await fetch('/book-slot/', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.success) {
            showSuccessMessage('Booking confirmed successfully!');
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showErrorMessage(data.message || 'Booking failed. Please try again.');
        }
    } catch (error) {
        showErrorMessage('Network error occurred. Please try again.');
    }
}

// Cancel a session
async function cancelSession(bookingId) {
    if (!confirm('Are you sure you want to cancel this session?')) {
        return;
    }

    try {
        const response = await fetch(`/cancel-booking/${bookingId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        const data = await response.json();
        
        if (data.success) {
            showSuccessMessage('Session cancelled successfully');
            // Force page reload after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showErrorMessage(data.message || 'Failed to cancel session');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorMessage('Network error occurred. Please try again.');
    }
}

// Function to update statistics
async function updateStatistics() {
    try {
        const response = await fetch('/get-user-sessions/');
        const data = await response.json();
        
        if (response.ok) {
            // Update upcoming sessions count
            const upcomingCount = document.querySelector('.upcoming-sessions-count');
            if (upcomingCount) {
                upcomingCount.textContent = data.upcoming_bookings.length;
            }
            
            // Update completed sessions count
            const completedCount = document.querySelector('.completed-sessions-count');
            if (completedCount) {
                completedCount.textContent = data.completed_bookings.length;
            }
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

// Add data-booking-id to session cards when displaying them
function displayUpcomingSessions(bookings) {
    const upcomingSessionsContainer = document.querySelector('.upcoming-sessions');
    upcomingSessionsContainer.innerHTML = '';

    if (bookings.length === 0) {
        upcomingSessionsContainer.innerHTML = '<p class="text-muted">No upcoming sessions</p>';
        return;
    }

    bookings.forEach(booking => {
        const sessionCard = document.createElement('div');
        sessionCard.className = 'session-card';
        sessionCard.dataset.bookingId = booking.id;  // Add this line
        
        sessionCard.innerHTML = `
            <div class="session-info">
                <h6>${booking.counselor.name}</h6>
                <p><i class="fas fa-calendar"></i> ${booking.date}</p>
                <p><i class="fas fa-clock"></i> ${booking.time}</p>
            </div>
            <div class="session-actions">
                <button class="btn btn-sm btn-outline-danger cancel-session">
                    <i class="fas fa-times"></i> Cancel
                </button>
            </div>
        `;
        
        upcomingSessionsContainer.appendChild(sessionCard);
    });

    // Add event listeners to new cancel buttons
    document.querySelectorAll('.cancel-session').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.session-card');
            if (card) {
                cancelSession(card.dataset.bookingId);
            }
        });
    });
}

async function fetchUserSessions() {
    try {
        const response = await fetch('/get-user-sessions/');
        const data = await response.json();

        if (response.ok) {
            updateUpcomingSessions(data.upcoming_bookings);
            updateCompletedSessions(data.completed_bookings);
            location.reload();
        } else {
            showErrorMessage(data.message || 'Error fetching user sessions');
        }
    } catch (error) {
        showErrorMessage('Network error occurred. Please try again.');
    }
}

function updateUpcomingSessions(bookings) {
    const upcomingSessionsContainer = document.querySelector('.upcoming-sessions');
    upcomingSessionsContainer.innerHTML = '';

    if (bookings.length === 0) {
        upcomingSessionsContainer.innerHTML = '<p class="text-muted">No upcoming sessions</p>';
    } else {
        bookings.forEach(booking => {
            // ... (existing code to create session cards)
        });

        // Add event listener for cancel buttons
        document.querySelectorAll('.cancel-session').forEach(button => {
            button.addEventListener('click', function() {
                const bookingId = this.closest('.session-card').dataset.bookingId;
                cancelSession(bookingId);
            });
        });
    }
}

function updateCompletedSessions(bookings) {
    const completedSessionsContainer = document.querySelector('.completed-sessions');
    completedSessionsContainer.innerHTML = '';

    if (bookings.length === 0) {
        completedSessionsContainer.innerHTML = '<p class="text-muted">No completed sessions</p>';
    } else {
        bookings.forEach(booking => {
            const sessionCard = document.createElement('div');
            sessionCard.className = 'session-card';

            sessionCard.innerHTML = `
                <div class="session-info">
                    <h6>${booking.counselor.name}</h6>
                    <p>${booking.date}</p>
                    <p>${booking.status}</p>
                </div>
            `;

            completedSessionsContainer.appendChild(sessionCard);
        });
    }
}
async function refreshUpcomingSessions() {
    try {
        const response = await fetch('/get-upcoming-sessions/');
        const data = await response.json();

        if (response.ok) {
            displayUpcomingSessions(data.bookings);
        } else {
            showErrorMessage(data.message || 'Error fetching upcoming sessions');
        }
    } catch (error) {
        showErrorMessage('Network error occurred. Please try again.');
    }
}

// Function to fetch and display upcoming sessions
async function fetchUpcomingSessions() {
    try {
        const response = await fetch('/get-upcoming-sessions/');
        const data = await response.json();

        if (response.ok) {
            displayUpcomingSessions(data.bookings);
        } else {
            showErrorMessage(data.message || 'Error fetching upcoming sessions');
        }
    } catch (error) {
        showErrorMessage('Network error occurred. Please try again.');
    }
}

// Reschedule a session
function rescheduleSession(bookingId) {
    // Store the booking ID for rescheduling
    window.bookingToReschedule = bookingId;
    // Show the reschedule modal
    new bootstrap.Modal(document.getElementById('rescheduleModal')).show();
}

// Reset booking modal
function resetBookingModal() {
    currentStep = 1;
    selectedDate = '';
    selectedTime = '';
    document.getElementById('bookingDate').value = '';
    document.querySelectorAll('.step').forEach(step => {
        step.style.display = 'none';
    });
    document.getElementById('step1').style.display = 'block';
    document.getElementById('nextStep').style.display = 'block';
    document.getElementById('confirmBooking').style.display = 'none';
}

// Initialize sidebar functionality
function initializeSidebar() {
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('content').classList.toggle('active');
        });
    }
    const settingsLink = document.querySelector('a[href="#"][onclick="openSettings()"]');
    if (settingsLink) {
        settingsLink.addEventListener('click', function(e) {
            e.preventDefault();
            openSettings();
        });
    }

    // initializeSettingsModal();
}

// Initialize mood selector
function initializeMoodSelector() {
    document.querySelectorAll('.mood-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.mood-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
        });
    });
}

// Utility Functions
function formatDate(dateString) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function showSuccessMessage(message) {
    // Create and show success alert
    const alert = createAlert('success', message);
    document.querySelector('.container-fluid').insertBefore(alert, document.querySelector('.container-fluid').firstChild);
}

function showErrorMessage(message) {
    // Create and show error alert
    const alert = createAlert('danger', message);
    document.querySelector('.container-fluid').insertBefore(alert, document.querySelector('.container-fluid').firstChild);
}

function createAlert(type, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Auto-remove alert after 3 seconds
    setTimeout(() => {
        alert.remove();
    }, 3000);
    
    return alert;
}



// Open settings modal
function openSettings() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    modal.show();
}

// Update settings
async function updateSettings() {
    try {
        const form = document.getElementById('settingsForm');
        const formData = new FormData(form);
        
        const response = await fetch('/update-student-settings/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Close the modal first
            bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
            
            // Show success message
            showSuccessMessage2(data.message);
            
            if (data.redirect) {
                // If password was changed, redirect to login page after a delay
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 2000);
            } else {
                // If only profile was updated, reload the current page
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        } else {
            showErrorMessage2(data.message);
        }
    } catch (error) {
        console.error('Error updating settings:', error);
        showErrorMessage2('Error updating settings');
    }
}

// Function to handle cancel button click
function handleCancel() {
    const form = document.getElementById('settingsForm');
    const passwordFields = form.querySelectorAll('input[type="password"]');
    const hasPasswordInput = Array.from(passwordFields).some(field => field.value.length > 0);
    
    if (hasPasswordInput) {
        if (confirm('Are you sure you want to cancel? Any unsaved changes will be lost.')) {
            // Clear password fields
            passwordFields.forEach(field => field.value = '');
            // Close the modal
            bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
        }
    } else {
        // If no password fields are filled, just close the modal
        bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
    }
    window.location.reload();
}

// Initialize settings modal
function initializeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        // Add event listener for cancel button
        const cancelBtn = modal.querySelector('button[data-bs-dismiss="modal"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', handleCancel);
        }

        // Add event listener for modal close button (X)
        const closeBtn = modal.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', handleCancel);
        }

        // Add event listener for clicking outside modal
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                handleCancel();
            }
        });
    }
}

// Show success message
function showSuccessMessage2(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '1050';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Show error message
function showErrorMessage2(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '1050';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}