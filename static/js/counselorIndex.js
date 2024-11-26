// Global variables
let bookingsTable;
let notificationCount = 0;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeFilters();
    initializeSlotForm();
    startAutoRefresh();
    checkForNewBookings();
});



// Auto refresh settings
const REFRESH_INTERVAL = 30000; // 30 seconds

function startAutoRefresh() {
    // Initial load
    refreshBookings();
    // Set up periodic refresh
    setInterval(refreshBookings, REFRESH_INTERVAL);
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

    initializeSettingsModal();
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
        
        const response = await fetch('/update-counselor-settings/', {
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
            showSuccessMessage(data.message);
            
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

// Show success message function
function showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '1050';  // Make sure it shows above the modal
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Show error message function
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

// Update the handleCancel function
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


// Initialize filters
function initializeFilters() {
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }
}

// Apply filters
async function applyFilters() {
    try {
        const filterForm = document.getElementById('filterForm');
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData);
        
        const response = await fetch(`/get-counselor-bookings/?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            updateBookingTable(data.bookings);
        } else {
            showErrorMessage(data.message || 'Failed to apply filters');
        }
    } catch (error) {
        console.error('Error applying filters:', error);
        showErrorMessage('Error applying filters');
    }
}


// Initialize slot form
function initializeSlotForm() {
    const slotForm = document.getElementById('slotForm');
    if (slotForm) {
        slotForm.addEventListener('submit', handleSlotUpdate);
    }
}

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

        // Add event listener for ESC key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && modal.classList.contains('show')) {
                handleCancel();
            }
        });
    }
}

// Refresh bookings
async function refreshBookings(filterData) {
    try {
        let url = '/get-counselor-bookings/';
        if (filterData) {
            const params = new URLSearchParams(filterData);
            url += '?' + params.toString();
        }

        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            updateBookingTable(data.bookings);
            // updateNotifications(data.new_bookings);
        }
    } catch (error) {
        console.error('Error refreshing bookings:', error);
    }
}

// Add/Update these functions in counselorDashboard.js

// View booking details
async function viewBookingDetails(bookingId) {
    try {
        const response = await fetch(`/get-booking-details/${bookingId}/`);
        const data = await response.json();
        
        if (data.success) {
            // Create detailed HTML with all student information
            const detailsHtml = `
                <div class="booking-details">
                    <div class="student-info mb-4">
                        <h6 class="text-primary mb-3">Student Information</h6>
                        <p><strong>Name:</strong> ${data.booking.client_name}</p>
                        <p><strong>Email:</strong> ${data.booking.client_email}</p>
                        <p><strong>Phone:</strong> ${data.booking.client_phone}</p>
                        <p><strong>Education:</strong> ${data.booking.client_education}</p>
                        <p><strong>Age:</strong> ${data.booking.client_age}</p>
                    </div>
                    
                    <div class="booking-info">
                        <h6 class="text-primary mb-3">Booking Information</h6>
                        <p><strong>Date:</strong> ${data.booking.date}</p>
                        <p><strong>Time:</strong> ${data.booking.time}</p>
                        <p><strong>Status:</strong> 
                            <span class="badge bg-${getBadgeColor(data.booking.status)}">
                                ${data.booking.status}
                            </span>
                        </p>
                    </div>
                </div>
            `;
            
            document.getElementById('bookingDetails').innerHTML = detailsHtml;
            new bootstrap.Modal(document.getElementById('bookingDetailsModal')).show();
        } else {
            showErrorMessage(data.message || 'Error fetching booking details');
        }
    } catch (error) {
        showErrorMessage('Error loading booking details');
        console.error('Error:', error);
    }
}



// Update the existing get-counselor-bookings view
function updateBookingTable(bookings) {
    const tbody = document.getElementById('bookingsTableBody');
    if (!tbody) return;

    let html = '';
    if (bookings.length === 0) {
        html = '<tr><td colspan="5" class="text-center">No bookings found</td></tr>';
    } else {
        bookings.forEach(booking => {
            html += `
                <tr data-booking-id="${booking.id}">
                    <td>${booking.client_name}</td>
                    <td>${booking.date}</td>
                    <td>${booking.time}</td>
                    <td>
                        <span class="badge bg-${getBadgeColor(booking.status)}">
                            ${capitalizeFirst(booking.status)}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="viewBookingDetails('${booking.id}')"
                                    title="View Details">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
    }
    tbody.innerHTML = html;
}

// Helper function to get badge color based on status
function getBadgeColor(status) {
    switch (status.toLowerCase()) {
        case 'scheduled':
            return 'primary';
        case 'cancelled':
            return 'danger';
        case 'completed':
            return 'success';
        default:
            return 'secondary';
    }
}

// Refresh bookings automatically
setInterval(refreshBookings, 30000); // Refresh every 30 seconds

// Cancel booking request
async function cancelBookingRequest(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }

    try {
        const response = await fetch(`/cancel-counselor-booking/${bookingId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccessMessage('Booking cancelled successfully');
            refreshBookings();
        } else {
            showErrorMessage(data.message || 'Failed to cancel booking');
        }
    } catch (error) {
        showErrorMessage('Error cancelling booking');
    }
}


// Handle slot update
async function handleSlotUpdate(e) {
    e.preventDefault();
    
    try {
        // Get all checked slots
        const checkedSlots = Array.from(document.querySelectorAll('input[name="slots[]"]:checked'))
            .map(checkbox => checkbox.value);
        
        // Create FormData
        const formData = new FormData();
        checkedSlots.forEach(slot => {
            formData.append('slots[]', slot);
        });
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const response = await fetch(window.location.pathname, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        
        if (response.ok) {
            // Show success message
            showSuccessMessage('Slots updated successfully');
            
            // Reload the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error('Failed to update slots');
        }
    } catch (error) {
        console.error('Error updating slots:', error);
        showErrorMessage('Error updating slots. Please try again.');
    }
}

// Check for new bookings
async function checkForNewBookings() {
    const response = await fetch('/get-new-bookings/');
    const data = await response.json();
    
    if (data.new_bookings > 0) {
        updateNotificationCount(data.new_bookings);
        updateNotificationList(data.bookings);
    }
}

// Update notification count
function updateNotificationCount(count) {
    const badge = document.querySelector('.notification-count');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

// Update notification list
function updateNotificationList(bookings) {
    const list = document.querySelector('.notification-list');
    if (!list) return;

    let html = '';
    bookings.forEach(booking => {
        html += `
            <a href="#" class="dropdown-item" onclick="viewBookingDetails('${booking.id}')">
                New booking from ${booking.client_name}
                <small class="text-muted d-block">
                    ${booking.date} at ${booking.time}
                </small>
            </a>
        `;
    });
    list.innerHTML = html;
}

// Export bookings
function exportBookings() {
    const table = document.querySelector('table');
    if (!table) return;

    const rows = Array.from(table.querySelectorAll('tr'));
    let csv = [];
    
    // Headers
    const headers = Array.from(rows[0].querySelectorAll('th'))
        .map(header => header.textContent.trim());
    csv.push(headers.join(','));
    
    // Data
    rows.slice(1).forEach(row => {
        const data = Array.from(row.querySelectorAll('td'))
            .map(cell => `"${cell.textContent.trim()}"`);
        csv.push(data.join(','));
    });

    // Download
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bookings-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Utility Functions
function capitalizeFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'danger');
}

function showMessage(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 3000);
}