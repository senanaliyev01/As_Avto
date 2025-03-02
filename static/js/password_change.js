document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('passwordChangeForm');
    const oldPassword = document.getElementById('oldPassword');
    const newPassword1 = document.getElementById('newPassword1');
    const newPassword2 = document.getElementById('newPassword2');
    const submitBtn = document.getElementById('submitBtn');
    const passwordMatch = document.getElementById('passwordMatch');
    const strengthText = document.getElementById('strengthText');
    const meterSections = document.querySelectorAll('.meter-section');
    
    // Şifrə tələbləri elementləri
    const requirements = {
        length: document.getElementById('length'),
        uppercase: document.getElementById('uppercase'),
        lowercase: document.getElementById('lowercase'),
        number: document.getElementById('number'),
        special: document.getElementById('special')
    };

    // Şifrə göstərmə/gizlətmə
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });

    // Şifrə gücünü yoxla
    function checkPasswordStrength(password) {
        let strength = 0;
        const checks = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /[0-9]/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Tələbləri yoxla və vizual göstər
        Object.keys(checks).forEach(key => {
            if (checks[key]) {
                strength++;
                requirements[key].classList.add('valid');
                requirements[key].querySelector('i').classList.remove('fa-circle');
                requirements[key].querySelector('i').classList.add('fa-check-circle');
            } else {
                requirements[key].classList.remove('valid');
                requirements[key].querySelector('i').classList.remove('fa-check-circle');
                requirements[key].querySelector('i').classList.add('fa-circle');
            }
        });

        // Gücü göstər
        meterSections.forEach((section, index) => {
            section.className = 'meter-section';
            if (index < strength) {
                if (strength <= 2) section.classList.add('weak');
                else if (strength <= 4) section.classList.add('medium');
                else section.classList.add('strong');
            }
        });

        // Mətn göstəricisini yenilə
        if (strength <= 2) strengthText.textContent = 'Zəif';
        else if (strength <= 4) strengthText.textContent = 'Orta';
        else strengthText.textContent = 'Güclü';

        return strength;
    }

    // Şifrələrin uyğunluğunu yoxla
    function checkPasswordsMatch() {
        const match = newPassword1.value === newPassword2.value;
        
        if (newPassword2.value) {
            passwordMatch.classList.add('visible');
            if (match) {
                passwordMatch.classList.add('match');
                passwordMatch.innerHTML = '<i class="fas fa-check-circle"></i><span>Şifrələr uyğundur</span>';
            } else {
                passwordMatch.classList.remove('match');
                passwordMatch.innerHTML = '<i class="fas fa-times-circle"></i><span>Şifrələr uyğun gəlmir</span>';
            }
        } else {
            passwordMatch.classList.remove('visible');
        }
        
        return match;
    }

    // Formanın təsdiqlənməsini yoxla
    function validateForm() {
        const strength = checkPasswordStrength(newPassword1.value);
        const match = checkPasswordsMatch();
        
        submitBtn.disabled = !(
            oldPassword.value && 
            newPassword1.value && 
            newPassword2.value && 
            strength >= 4 && 
            match
        );
    }

    // Event listeners
    [oldPassword, newPassword1, newPassword2].forEach(input => {
        input.addEventListener('input', validateForm);
    });

    // Alert mesajlarının avtomatik bağlanması
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 3000);
    });

    // Form submit
    form.addEventListener('submit', function(e) {
        if (!submitBtn.disabled) {
            const strength = checkPasswordStrength(newPassword1.value);
            if (strength < 4) {
                e.preventDefault();
                alert('Zəhmət olmasa daha güclü şifrə seçin!');
            }
        } else {
            e.preventDefault();
        }
    });
});