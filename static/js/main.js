// Add Bootstrap form validation
(function () {
    'use strict'
    
    // Fetch all forms that need validation
    var forms = document.querySelectorAll('.needs-validation')
    
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
})()

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)')
        alerts.forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease-in-out'
            alert.style.opacity = '0'
            setTimeout(function() {
                alert.remove()
            }, 500)
        })
    }, 5000)
})

// Initialize tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Form field character counter
document.querySelectorAll('textarea[maxlength]').forEach(function(textarea) {
    var counter = document.createElement('small')
    counter.className = 'form-text text-muted'
    textarea.parentNode.appendChild(counter)
    
    function updateCounter() {
        var remaining = textarea.maxLength - textarea.value.length
        counter.textContent = remaining + ' characters remaining'
    }
    
    textarea.addEventListener('input', updateCounter)
    updateCounter()
})

// Blood group availability check
function checkBloodAvailability(bloodGroup) {
    const inventoryElements = document.querySelectorAll('.blood-inventory')
    let available = false
    
    inventoryElements.forEach(function(element) {
        if (element.dataset.bloodGroup === bloodGroup && 
            parseInt(element.dataset.units) > 0) {
            available = true
        }
    })
    
    return available
}

// Phone number formatter
function formatPhoneNumber(input) {
    let cleaned = input.value.replace(/\D/g, '')
    let match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
    
    if (match) {
        input.value = '(' + match[1] + ') ' + match[2] + '-' + match[3]
    }
}

// Date validator for donor registration
function validateDonorAge(birthDate) {
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--
    }
    
    return age >= 18 && age <= 65
} 