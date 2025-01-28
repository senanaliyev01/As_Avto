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
});