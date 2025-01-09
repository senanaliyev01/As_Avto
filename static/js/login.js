document.addEventListener('DOMContentLoaded', function() {
    // Form elemanları
    const form = document.querySelector('.login-form');
    const inputs = document.querySelectorAll('.input-wrap input');
    const passwordInput = document.getElementById('passwordInput');
    const togglePassword = document.querySelector('.toggle-password');
    const loginBtn = document.querySelector('.login-btn');
    let passwordVisible = false;

    // Input focus efektleri
    inputs.forEach(input => {
        // Başlangıçta değer varsa label'ı yukarı taşı
        if (input.value !== '') {
            input.parentElement.classList.add('focused');
        }

        // Focus olduğunda
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });

        // Focus'tan çıkıldığında
        input.addEventListener('blur', () => {
            if (input.value === '') {
                input.parentElement.classList.remove('focused');
            }
        });
    });

    // Şifre göster/gizle
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function(e) {
            e.preventDefault(); // Formun gönderilmesini engelle
            
            // Şifre görünürlüğünü değiştir
            passwordVisible = !passwordVisible;
            
            // Input tipini değiştir
            passwordInput.type = passwordVisible ? 'text' : 'password';
            
            // İkonu değiştir
            const icon = this.querySelector('i');
            if (passwordVisible) {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        });
    }

    // Form gönderimi
    if (form) {
        form.addEventListener('submit', function(e) {
            loginBtn.classList.add('loading');
            loginBtn.disabled = true;
        });
    }

    // Alert mesajları
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transform = 'translateX(100%)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Arka plan animasyonu
    const circles = document.querySelectorAll('.circles li');
    circles.forEach(circle => {
        const delay = Math.random() * 10;
        const duration = Math.random() * 10 + 10;
        circle.style.animationDelay = `${delay}s`;
        circle.style.animationDuration = `${duration}s`;
    });
});