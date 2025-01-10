document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    const passwordInput = form.querySelector('input[name="password"]');
    const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    const modal = document.getElementById('messageModal');
    const modalMessage = document.getElementById('modalMessage');
    const closeModal = document.querySelector('.close');

    // CSRF token əldə et
    function getCSRFToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }

    // Şifrə tələbləri elementləri
    const lengthReq = document.getElementById('length');
    const uppercaseReq = document.getElementById('uppercase');
    const numberReq = document.getElementById('number');
    const specialReq = document.getElementById('special');

    // Şifrə göstər/gizlə
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        });
    });

    // Şifrə tələblərini yoxla
    function checkPasswordRequirements(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Vizual göstəricilər
        lengthReq.classList.toggle('valid', requirements.length);
        uppercaseReq.classList.toggle('valid', requirements.uppercase);
        numberReq.classList.toggle('valid', requirements.number);
        specialReq.classList.toggle('valid', requirements.special);

        // İkonları yenilə
        document.querySelectorAll('.password-requirements li').forEach(li => {
            const icon = li.querySelector('i');
            if (li.classList.contains('valid')) {
                icon.className = 'fas fa-check-circle';
            } else {
                icon.className = 'fas fa-circle';
            }
        });

        return Object.values(requirements).every(req => req);
    }

    // Şifrə dəyişdikdə tələbləri yoxla
    passwordInput.addEventListener('input', function() {
        checkPasswordRequirements(this.value);
    });

    // Modal funksiyaları
    function showModal(message, isSuccess = true) {
        modalMessage.textContent = message;
        const modalIcon = document.querySelector('.modal-icon');
        modalIcon.className = 'modal-icon ' + (isSuccess ? 'success' : 'error');
        modalIcon.innerHTML = isSuccess ? 
            '<i class="fas fa-check-circle"></i>' : 
            '<i class="fas fa-exclamation-circle"></i>';
        modal.style.display = 'block';
    }

    function closeModalFunc() {
        modal.style.display = 'none';
    }

    closeModal.addEventListener('click', closeModalFunc);
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModalFunc();
        }
    });

    // Form göndərilməsi
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Loading göstər
        const submitBtn = form.querySelector('.register-btn');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;

        try {
            const formData = new FormData(form);
            const response = await fetch('/register/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            console.log('Server cavabı:', data);

            if (data.status === 'success') {
                showModal(data.message, true);
                form.reset();
                setTimeout(() => {
                    window.location.href = '/login/';
                }, 3000);
            } else {
                showModal(data.message, false);
            }
        } catch (error) {
            console.error('Xəta:', error);
            showModal('Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.', false);
        } finally {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    });

    // Input animasiyaları
    document.querySelectorAll('.input-wrap input').forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
            if (this.value) {
                this.parentElement.classList.add('has-value');
            } else {
                this.parentElement.classList.remove('has-value');
            }
        });

        // Placeholder əlavə et
        input.setAttribute('placeholder', ' ');
    });
}); 