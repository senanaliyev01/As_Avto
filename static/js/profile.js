document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const profileImage = document.getElementById('profileImage');
    const imageContainer = document.querySelector('.profile-image-container');

    if (imageContainer && imageInput && profileImage) {
        imageContainer.addEventListener('click', () => {
            imageInput.click();
        });

        imageInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const formData = new FormData();
                formData.append('sekil', this.files[0]);
                
                // Loading effekti
                profileImage.style.opacity = '0.5';
                
                fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        profileImage.src = data.image_url + '?t=' + new Date().getTime();
                        showAlert('success', 'Profil şəkli uğurla yeniləndi!');
                    } else {
                        showAlert('error', data.error || 'Xəta baş verdi!');
                    }
                })
                .catch(error => {
                    console.error('Xəta:', error);
                    showAlert('error', 'Şəkil yüklənərkən xəta baş verdi!');
                })
                .finally(() => {
                    profileImage.style.opacity = '1';
                });
            }
        });
    }
});

// Alert göstərmə funksiyası
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.messages-container').appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}

// Logout funksiyaları
function logout() {
    const dialog = document.getElementById('logoutDialog');
    if (dialog) {
        dialog.classList.add('show');
        dialog.querySelector('.logout-confirm-content').classList.add('show');
    }
}

function closeLogoutDialog() {
    const dialog = document.getElementById('logoutDialog');
    if (dialog) {
        dialog.classList.remove('show');
        dialog.querySelector('.logout-confirm-content').classList.remove('show');
    }
}

function confirmLogout() {
    const content = document.querySelector('.logout-confirm-content');
    if (content) {
        content.innerHTML = `
            <div class="success-icon-wrapper">
                <i class="fas fa-check success-icon"></i>
            </div>
            <h4 class="logout-success">Uğurla çıxış edildi!</h4>
            <div class="redirect-message">
                <i class="fas fa-spinner fa-spin"></i>
                <span>Yönləndirilirsiniz...</span>
            </div>
        `;

        fetch('/istifadeciler/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(() => {
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        });
    }
}