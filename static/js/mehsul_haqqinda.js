document.addEventListener('DOMContentLoaded', function() {
    const productImage = document.getElementById('productImage');
    const brandImage = document.getElementById('brandImage');
    
    // Hər şəkil üçün ayrı rotasiya dəyərləri
    const rotations = {
        product: { x: 0, y: 0 },
        brand: { x: 0, y: 0 }
    };
    
    let isDragging = false;
    let startX, startY;
    let currentElement = null;
    
    function handleStart(e, element, type) {
        isDragging = true;
        currentElement = { element, type };
        startX = e.pageX || e.touches[0].pageX;
        startY = e.pageY || e.touches[0].pageY;
        element.style.transition = 'none';
        e.preventDefault();
    }
    
    function handleMove(e) {
        if (!isDragging || !currentElement) return;
        
        e.preventDefault();
        const pageX = e.pageX || e.touches[0].pageX;
        const pageY = e.pageY || e.touches[0].pageY;
        
        const deltaX = pageX - startX;
        const deltaY = pageY - startY;
        
        // Fırlanma limitləri
        rotations[currentElement.type].y = Math.max(-180, Math.min(180, deltaX * 0.5));
        rotations[currentElement.type].x = Math.max(-30, Math.min(30, -deltaY * 0.5));
        
        currentElement.element.style.transform = `
            perspective(1000px)
            rotateY(${rotations[currentElement.type].y}deg)
            rotateX(${rotations[currentElement.type].x}deg)
        `;
    }
    
    function handleEnd() {
        if (!isDragging || !currentElement) return;
        
        isDragging = false;
        currentElement.element.style.transition = 'transform 0.5s ease';
        currentElement.element.style.transform = 'perspective(1000px) rotateY(0) rotateX(0)';
        
        // Rotasiya dəyərlərini sıfırla
        rotations[currentElement.type].x = 0;
        rotations[currentElement.type].y = 0;
        
        currentElement = null;
    }
    
    // Mouse events
    if (productImage) {
        productImage.addEventListener('mousedown', (e) => handleStart(e, productImage, 'product'));
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('mouseleave', handleEnd);
    }
    
    if (brandImage) {
        brandImage.addEventListener('mousedown', (e) => handleStart(e, brandImage, 'brand'));
        document.addEventListener('mousemove', handleMove);
        document.addEventListener('mouseup', handleEnd);
        document.addEventListener('mouseleave', handleEnd);
    }
    
    // Touch events
    if (productImage) {
        productImage.addEventListener('touchstart', (e) => handleStart(e, productImage, 'product'));
        productImage.addEventListener('touchmove', handleMove);
        productImage.addEventListener('touchend', handleEnd);
        productImage.addEventListener('touchcancel', handleEnd);
    }
    
    if (brandImage) {
        brandImage.addEventListener('touchstart', (e) => handleStart(e, brandImage, 'brand'));
        brandImage.addEventListener('touchmove', handleMove);
        brandImage.addEventListener('touchend', handleEnd);
        brandImage.addEventListener('touchcancel', handleEnd);
    }
    
    // Şəkillərin sürüklənməsini əngəlləmək
    document.addEventListener('dragstart', (e) => e.preventDefault());
    
    // Məhsul məlumatlarının animasiyası
    const specItems = document.querySelectorAll('.spec-item');
    specItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, 100 + (index * 100));
    });
    
    // Səbətə əlavə et düyməsinin animasiyası
    const cartButton = document.querySelector('.cart-icon');
    if (cartButton) {
        cartButton.style.opacity = '0';
        cartButton.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            cartButton.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            cartButton.style.opacity = '1';
            cartButton.style.transform = 'translateY(0)';
        }, 100 + (specItems.length * 100));
        
        // Səbətə əlavə et düyməsinə klik hadisəsi
        cartButton.addEventListener('click', function(e) {
            const productId = this.getAttribute('data-product-id');
            
            // Animasiya effekti
            this.classList.add('adding-to-cart');
            
            setTimeout(() => {
                this.classList.remove('adding-to-cart');
            }, 1000);
        });
    }
    
    // OEM kodlarının hover effekti
    const oemCodes = document.querySelectorAll('.oem-code');
    oemCodes.forEach(code => {
        code.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
        });
        
        code.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // Responsive dizayn üçün məhsul başlığının pozisiyasını tənzimləmək
    function adjustTitlePosition() {
        const titleOverlay = document.querySelector('.product-title-overlay');
        const imageContainer = document.querySelector('.product-image-container');
        
        if (titleOverlay && imageContainer && window.innerWidth <= 1024) {
            titleOverlay.style.position = 'relative';
            titleOverlay.style.top = '0';
            titleOverlay.style.right = '0';
            titleOverlay.style.maxWidth = '100%';
            titleOverlay.style.marginBottom = '1.5rem';
        } else if (titleOverlay && imageContainer) {
            titleOverlay.style.position = 'absolute';
            titleOverlay.style.top = '20px';
            titleOverlay.style.right = '20px';
            titleOverlay.style.maxWidth = '60%';
            titleOverlay.style.marginBottom = '0';
        }
    }
    
    // İlkin yükləmə və pəncərə ölçüsü dəyişdikdə
    adjustTitlePosition();
    window.addEventListener('resize', adjustTitlePosition);
});