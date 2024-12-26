  // Hazırki saatı göstərmək
        function updateCurrentTime() {
            const currentTimeElement = document.getElementById('current-time');
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            currentTimeElement.textContent = `${hours}:${minutes}:${seconds}`;
        }

        // Hazırki saatı hər saniyə yeniləmək
        setInterval(updateCurrentTime, 1000);
        updateCurrentTime();

document.addEventListener("DOMContentLoaded", () => {
    const sliders = document.querySelectorAll(".slider ");

    sliders.forEach((slider) => {
        // Sonsuz dövr üçün elementlərin təkrarlanması
        slider.innerHTML += slider.innerHTML;

        let scrollAmount = 0;
        const slideInterval = setInterval(() => {
            if (scrollAmount < slider.scrollWidth / 2) { // Yalnız yarım eni keçmək üçün
                scrollAmount += 2; // Sürəti tənzimləyin
            } else {
                scrollAmount = 0; // Yenidən başlayır
            }
            slider.scrollTo({
                left: scrollAmount,
                behavior: "smooth",
            });
        }, 50); // İstədiyiniz interval
    });
});


document.addEventListener("DOMContentLoaded", () => {
    const sliders = document.querySelectorAll(".slider, .partner-slider");

    sliders.forEach((slider) => {
        // Sonsuz dövr üçün elementlərin təkrarlanması
        slider.innerHTML += slider.innerHTML;

        let scrollAmount = 0;
        const slideInterval = setInterval(() => {
            if (scrollAmount < slider.scrollWidth / 2) { // Yalnız yarım eni keçmək üçün
                scrollAmount += 2; // Sürəti tənzimləyin
            } else {
                scrollAmount = 0; // Yenidən başlayır
            }
            slider.scrollTo({
                left: scrollAmount,
                behavior: "smooth",
            });
        }, 50); // İstədiyiniz interval
    });
});


window.addEventListener('DOMContentLoaded', () => {
    const welcomeCard = document.getElementById('welcomeCard');

    // Giriş uğurlu olduqda kartı göstərmək
    setTimeout(() => {
        welcomeCard.style.display = 'block'; // Kartı göstərmək
    }, 1000); // 1 saniyə sonra kartı göstər
});
