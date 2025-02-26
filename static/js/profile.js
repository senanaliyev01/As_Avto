document.addEventListener('DOMContentLoaded', function() {
    // Dropdown menyu funksionallığı
    const profileToggle = document.querySelector('.profile-toggle');
    const profileDropdown = document.querySelector('.profile-dropdown');

    if (profileToggle && profileDropdown) {
        profileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            profileDropdown.classList.toggle('active');
        });

        // Səhifənin başqa yerinə kliklədikdə dropdown-ı bağla
        document.addEventListener('click', function(e) {
            if (!profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove('active');
            }
        });

        // ESC düyməsinə basıldıqda dropdown-ı bağla
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                profileDropdown.classList.remove('active');
            }
        });
    }

    // Mövcud profil şəkli funksionallığı
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