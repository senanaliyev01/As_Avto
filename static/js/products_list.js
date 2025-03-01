// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add to cart with quantity function
function addToCartWithQuantity(event, productId, element) {
    event.preventDefault();
    
    // Get quantity input
    const quantityInput = element.parentElement.querySelector('.quantity-input');
    const quantity = parseInt(quantityInput.value);
    
    // Validate quantity
    if (isNaN(quantity) || quantity < 1) {
        showAnimatedMessage('Xahiş edirik düzgün miqdar daxil edin', true);
        return;
    }

    // Send AJAX request
    fetch('/sebet/elave/' + productId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAnimatedMessage('Məhsul səbətə əlavə edildi', false, data.mehsul);
            // Update cart count if needed
            if (typeof updateCartCount === 'function') {
                updateCartCount();
            }
        } else {
            showAnimatedMessage(data.error || 'Xəta baş verdi', true);
        }
    })
    .catch(error => {
        showAnimatedMessage('Xəta baş verdi', true);
        console.error('Error:', error);
    });
}

// Modal image functionality
function openModal(src) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.style.display = "flex";
    modalImg.src = src;
    
    // Add open class for animation
    setTimeout(() => {
        modal.classList.add('modal-open');
    }, 10);
}

// Close modal when clicking on X or outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('imageModal');
    const closeBtn = document.querySelector('.close-modal');
    
    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.classList.remove('modal-open');
            modal.classList.add('modal-closing');
            setTimeout(() => {
                modal.style.display = "none";
                modal.classList.remove('modal-closing');
            }, 300);
        }
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.classList.remove('modal-open');
            modal.classList.add('modal-closing');
            setTimeout(() => {
                modal.style.display = "none";
                modal.classList.remove('modal-closing');
            }, 300);
        }
    }
});