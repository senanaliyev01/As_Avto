/**
 * Novruz Bayramı JavaScript
 * Bu fayl Novruz bayramı elementlərini dinamik olaraq əlavə etmək və ləğv etmək üçün istifadə olunur.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Novruz elementlərini əlavə et
    addNovruzElements();
    
    // Novruz elementlərini ləğv etmək üçün düymə əlavə et
    addToggleButton();
});

/**
 * Header-ə Novruz bayramı elementlərini əlavə edir
 */
function addNovruzElements() {
    const header = document.querySelector('header');
    
    if (!header) return;
    
    // Əgər elementlər artıq mövcuddursa, əlavə etmə
    if (document.querySelector('.novruz-grass')) return;
    
    // Otluq elementi
    const grass = document.createElement('div');
    grass.className = 'novruz-grass';
    
    // Taxta elementi
    const wood = document.createElement('div');
    wood.className = 'novruz-wood';
    
    // Alov elementi
    const fire = document.createElement('div');
    fire.className = 'novruz-fire';
    
    // Elementləri header-ə əlavə et
    header.appendChild(grass);
    header.appendChild(wood);
    header.appendChild(fire);
    
    // Novruz elementlərinin aktiv olduğunu localStorage-də saxla
    localStorage.setItem('novruzActive', 'true');
}

/**
 * Novruz bayramı elementlərini silir
 */
function removeNovruzElements() {
    const elements = document.querySelectorAll('.novruz-grass, .novruz-wood, .novruz-fire');
    
    elements.forEach(element => {
        element.remove();
    });
    
    // Novruz elementlərinin deaktiv olduğunu localStorage-də saxla
    localStorage.setItem('novruzActive', 'false');
}

/**
 * Novruz elementlərini göstərmək/gizlətmək üçün düymə əlavə edir
 */
function addToggleButton() {
    // Əgər düymə artıq mövcuddursa, əlavə etmə
    if (document.querySelector('#novruz-toggle')) return;
    
    const header = document.querySelector('header .header-right');
    
    if (!header) return;
    
    // Düymə yarat
    const button = document.createElement('a');
    button.id = 'novruz-toggle';
    button.href = '#';
    button.className = 'novruz-toggle-button';
    button.innerHTML = '<i class="fas fa-fire"></i> Novruz';
    
    // Düyməyə klik hadisəsi əlavə et
    button.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Novruz elementlərinin aktiv olub-olmadığını yoxla
        const isActive = localStorage.getItem('novruzActive') === 'true';
        
        if (isActive) {
            removeNovruzElements();
            button.innerHTML = '<i class="fas fa-fire"></i> Novruz (Deaktiv)';
        } else {
            addNovruzElements();
            button.innerHTML = '<i class="fas fa-fire"></i> Novruz (Aktiv)';
        }
    });
    
    // Düyməni header-ə əlavə et
    header.appendChild(button);
    
    // Düymənin mətnini tənzimlə
    const isActive = localStorage.getItem('novruzActive') === 'true';
    button.innerHTML = isActive ? 
        '<i class="fas fa-fire"></i> Novruz (Aktiv)' : 
        '<i class="fas fa-fire"></i> Novruz (Deaktiv)';
    
    // Əgər localStorage-də məlumat yoxdursa və ya aktivdirsə, elementləri əlavə et
    if (isActive || localStorage.getItem('novruzActive') === null) {
        addNovruzElements();
    }
}

// Səhifə yüklənəndə Novruz elementlərinin vəziyyətini yoxla
window.addEventListener('load', function() {
    const isActive = localStorage.getItem('novruzActive');
    
    // Əgər localStorage-də məlumat yoxdursa və ya aktivdirsə, elementləri əlavə et
    if (isActive === 'true' || isActive === null) {
        addNovruzElements();
    }
}); 