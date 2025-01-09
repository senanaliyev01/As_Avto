// Səhifə yüklənəndə animasiyaları başlat
document.addEventListener('DOMContentLoaded', () => {
    // Scroll animasiyaları
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.manager-card, .delivery-card, .location-container');
        
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            
            if (elementTop < window.innerHeight && elementBottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Elementlərə başlanğıc stilləri əlavə et
    const elements = document.querySelectorAll('.manager-card, .delivery-card, .location-container');
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(50px)';
        element.style.transition = 'all 0.6s ease-out';
    });

    // Scroll hadisəsini izlə
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // İlk yükləmədə də yoxla

    // Navbar scroll effekti
    let prevScrollPos = window.pageYOffset;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const currentScrollPos = window.pageYOffset;
        
        if (prevScrollPos > currentScrollPos) {
            navbar.style.top = '0';
        } else {
            navbar.style.top = '-100px';
        }
        
        if (currentScrollPos > 100) {
            navbar.style.backgroundColor = 'rgba(23, 42, 69, 0.95)';
            navbar.style.backdropFilter = 'blur(8px)';
        } else {
            navbar.style.backgroundColor = 'var(--secondary-color)';
            navbar.style.backdropFilter = 'none';
        }
        
        prevScrollPos = currentScrollPos;
    });

    // Telefon nömrəsini kopyalama funksiyası
    const phoneNumber = document.querySelector('a[href^="tel:"]');
    phoneNumber.addEventListener('click', (e) => {
        e.preventDefault();
        const number = phoneNumber.href.replace('tel:', '');
        navigator.clipboard.writeText(number).then(() => {
            showNotification('Telefon nömrəsi kopyalandı!');
        });
    });

    // Email ünvanını kopyalama funksiyası
    const email = document.querySelector('a[href^="mailto:"]');
    email.addEventListener('click', (e) => {
        e.preventDefault();
        const emailAddress = email.href.replace('mailto:', '');
        navigator.clipboard.writeText(emailAddress).then(() => {
            showNotification('Email ünvanı kopyalandı!');
        });
    });
});

// Bildiriş göstərmə funksiyası
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Xəritə yükləmə optimizasiyası
const mapIframe = document.querySelector('.map-container iframe');
if (mapIframe) {
    mapIframe.setAttribute('loading', 'lazy');
}

// Şəkillərin lazy loading
document.querySelectorAll('img').forEach(img => {
    img.setAttribute('loading', 'lazy');
});