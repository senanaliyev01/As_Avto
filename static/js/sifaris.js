document.addEventListener('DOMContentLoaded', function() {
    // Initialize progress tracker
    initProgressTracker();
    
    // Add hover effects to table rows
    addTableHoverEffects();
    
    // Initialize payment card animations
    initPaymentCard();
});

// Progress Tracker Initialization
function initProgressTracker() {
    const steps = document.querySelectorAll('.progress-step');
    
    steps.forEach((step, index) => {
        if (step.classList.contains('current') || step.classList.contains('completed')) {
            animateStep(step, index);
        }
        
        // Add hover effects
        addStepHoverEffect(step);
    });
}

function animateStep(step, index) {
    setTimeout(() => {
        // Animate icon
        const icon = step.querySelector('.step-icon');
        if (icon) {
            icon.style.transform = 'scale(1.1)';
            icon.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        // Animate check icon if completed
        if (step.classList.contains('completed')) {
            const check = step.querySelector('.step-check');
            if (check) {
                check.style.opacity = '0';
                check.style.transform = 'scale(0)';
                
                setTimeout(() => {
                    check.style.opacity = '1';
                    check.style.transform = 'scale(1)';
                }, 200);
            }
        }
    }, index * 200);
}

function addStepHoverEffect(step) {
    step.addEventListener('mouseenter', () => {
        if (step.classList.contains('current') || step.classList.contains('completed')) {
            const icon = step.querySelector('.step-icon');
            if (icon) {
                icon.style.transform = 'scale(1.15)';
            }
        }
    });
    
    step.addEventListener('mouseleave', () => {
        if (step.classList.contains('current') || step.classList.contains('completed')) {
            const icon = step.querySelector('.step-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1)';
            }
        }
    });
}

// Table Interactions
function addTableHoverEffects() {
    const rows = document.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'translateX(5px)';
            row.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'translateX(0)';
        });
    });
    
    // Add sorting functionality
    addTableSorting();
}

function addTableSorting() {
    const headers = document.querySelectorAll('th');
    
    headers.forEach((header, index) => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const sortedRows = rows.sort((a, b) => {
                const aValue = a.children[index].textContent;
                const bValue = b.children[index].textContent;
                
                // Check if values are numbers
                const aNum = parseFloat(aValue);
                const bNum = parseFloat(bValue);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return aNum - bNum;
                }
                
                return aValue.localeCompare(bValue);
            });
            
            // Clear and re-append rows
            tbody.innerHTML = '';
            sortedRows.forEach(row => tbody.appendChild(row));
        });
    });
}

// Payment Card Animations
function initPaymentCard() {
    const paymentRows = document.querySelectorAll('.payment-row');
    
    paymentRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transform = 'scale(1.02)';
            row.style.transition = 'transform 0.2s ease';
        });
        
        row.addEventListener('mouseleave', () => {
            row.style.transform = 'scale(1)';
        });
    });
}

// Prevent browser back button
history.pushState(null, '', location.href);
window.onpopstate = function() {
    history.pushState(null, '', location.href);
};

function createSmoke(truckContainer) {
    const smoke = document.createElement('div');
    smoke.className = 'smoke';
    truckContainer.appendChild(smoke);
    
    setTimeout(() => {
        smoke.remove();
    }, 2000);
}

// Tüstü effektini başlat
document.querySelectorAll('.truck-container').forEach(container => {
    setInterval(() => {
        createSmoke(container);
    }, 300);
});

// Status badge-ləri üçün pulsing effekt
const badges = document.querySelectorAll('.status-badge');
badges.forEach(badge => {
    setInterval(() => {
        badge.style.transform = 'scale(1.05)';
        setTimeout(() => {
            badge.style.transform = 'scale(1)';
        }, 200);
    }, 3000);
});

// Success check ikonları üçün animasiya
document.querySelectorAll('.success-check-icon').forEach(icon => {
    icon.addEventListener('mouseover', () => {
        icon.classList.add('tada');
    });
    
    icon.addEventListener('mouseout', () => {
        icon.classList.remove('tada');
    });
});
