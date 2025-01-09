// Kar animasyonunun zaten başlatılıp başlatılmadığını kontrol et
if (!window.snowAnimationStarted) {
    window.snowAnimationStarted = true;

    function createSnowflake() {
        const snowflake = document.createElement('div');
        snowflake.classList.add('snowflake');
        
        // Təsadüfi qar dənəcəyi seç
        const snowflakeTypes = ['❄', '❅', '❆', '✻', '✺', '❉'];
        const randomType = snowflakeTypes[Math.floor(Math.random() * snowflakeTypes.length)];
        snowflake.innerHTML = randomType;
        
        snowflake.style.left = Math.random() * 100 + '%';
        snowflake.style.opacity = Math.random() * 0.6 + 0.4;
        snowflake.style.fontSize = (Math.random() * 15 + 8) + 'px';
        snowflake.style.animationDuration = (Math.random() * 3 + 2) + 's, ' + (Math.random() * 2 + 2) + 's';
        
        document.body.appendChild(snowflake);

        setTimeout(() => {
            if (snowflake && snowflake.parentNode) {
                snowflake.parentNode.removeChild(snowflake);
            }
        }, 10000);
    }

    function startSnowAnimation() {
        // Ekran genişliğine göre kar tanesi sayısını ayarla
        const interval = window.innerWidth < 768 ? 400 : 200; // Mobilde daha az kar tanesi
        setInterval(createSnowflake, interval);
    }

    // Sayfa yüklendiğinde animasyonu başlat
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startSnowAnimation);
    } else {
        startSnowAnimation();
    }
}