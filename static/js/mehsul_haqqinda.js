document.addEventListener('DOMContentLoaded', function() {
    const productImage = document.getElementById('productImage');
    const brandImage = document.getElementById('brandImage');
    
    // Şəkil effektləri üçün dəyərlər
    const rotations = {
        product: { x: 0, y: 0 },
        brand: { x: 0, y: 0 }
    };
    
    let isDragging = false;
    let startX, startY;
    let currentElement = null;
    
    // Şəkil fırlanma funksiyaları
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
    
    // Səbətə əlavə et düyməsi üçün animasiya
    const addToCartBtn = document.querySelector('.add-to-cart .btn-primary');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function(e) {
            // Səbətə əlavə edildi animasiyası
            const icon = this.querySelector('i');
            icon.classList.add('animate__animated', 'animate__bounceIn');
            
            setTimeout(() => {
                icon.classList.remove('animate__animated', 'animate__bounceIn');
            }, 1000);
            
            // Səbət sayğacını yeniləmək üçün AJAX sorğusu burada olacaq
            // Bu nümunə üçün sadəcə animasiya göstəririk
        });
    }
    
    // OEM kodları üçün tooltip
    const oemCodes = document.querySelectorAll('.oem-code');
    oemCodes.forEach(code => {
        code.setAttribute('title', 'Alternativ OEM kodu');
        code.style.cursor = 'help';
    });
    
    // Cədvəl sıralarını filtrlə
    const tableFilter = document.createElement('input');
    const compatibleModelsTable = document.querySelector('.compatible-models table');
    
    if (compatibleModelsTable) {
        tableFilter.type = 'text';
        tableFilter.className = 'form-control mb-3';
        tableFilter.placeholder = 'Avtomobil və ya model adına görə axtar...';
        
        const tableContainer = compatibleModelsTable.parentElement;
        tableContainer.insertBefore(tableFilter, compatibleModelsTable);
        
        tableFilter.addEventListener('keyup', function() {
            const filterValue = this.value.toLowerCase();
            const rows = compatibleModelsTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.indexOf(filterValue) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Səhifə yüklənəndə yumşaq animasiya
    const productContainer = document.querySelector('.mehsul-container');
    const productDescription = document.querySelector('.product-description');
    const compatibleModels = document.querySelector('.compatible-models');
    const brandInfo = document.querySelector('.brand-info');
    
    if (productContainer) {
        productContainer.style.opacity = '0';
        productContainer.style.transform = 'translateY(20px)';
        productContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            productContainer.style.opacity = '1';
            productContainer.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Digər bölmələr üçün scroll animasiyası
    function animateOnScroll(element, delay) {
        if (!element) return;
        
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                    }, delay);
                    observer.unobserve(element);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(element);
    }
    
    animateOnScroll(productDescription, 200);
    animateOnScroll(compatibleModels, 300);
    animateOnScroll(brandInfo, 400);
});