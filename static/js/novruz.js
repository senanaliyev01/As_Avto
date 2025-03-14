// Novruz Bayramı JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Novruz elementlərinin aktivləşdirilməsi
    initNovruz();
    
    // Toggle düyməsinin işləməsi
    setupNovruzToggle();
    
    // Local Storage-dən vəziyyəti yoxla
    checkNovruzState();
});

// Novruz elementlərini yaratmaq
function initNovruz() {
    const header = document.querySelector('header');
    
    if (!header) return;
    
    // Header-in position-unu relative et
    header.style.position = 'relative';
    
    // Novruz başlığı
    const novruzTitle = document.createElement('div');
    novruzTitle.className = 'novruz-title';
    novruzTitle.textContent = 'Novruz Bayramınız Mübarək!';
    novruzTitle.id = 'novruz-title';
    
    // Otluq
    const grassContainer = document.createElement('div');
    grassContainer.className = 'grass-container';
    grassContainer.id = 'grass-container';
    
    const grass = document.createElement('div');
    grass.className = 'grass';
    grassContainer.appendChild(grass);
    
    // Alov
    const fireContainer = document.createElement('div');
    fireContainer.className = 'fire-container';
    fireContainer.id = 'fire-container';
    
    const fire = document.createElement('img');
    fire.className = 'fire';
    fire.src = '/static/img/novruz/fire.gif';
    fire.alt = 'Alov';
    fireContainer.appendChild(fire);
    
    // Taxta
    const woodContainer = document.createElement('div');
    woodContainer.className = 'wood-container';
    woodContainer.id = 'wood-container';
    
    const wood = document.createElement('img');
    wood.className = 'wood';
    wood.src = '/static/img/novruz/wood.png';
    wood.alt = 'Taxta';
    woodContainer.appendChild(wood);
    
    // Səməni
    const semeniContainer = document.createElement('div');
    semeniContainer.className = 'semeni-container';
    semeniContainer.id = 'semeni-container';
    
    const semeni = document.createElement('img');
    semeni.className = 'semeni';
    semeni.src = '/static/img/novruz/semeni.png';
    semeni.alt = 'Səməni';
    semeniContainer.appendChild(semeni);
    
    // Toggle düyməsi
    const toggleButton = document.createElement('button');
    toggleButton.className = 'novruz-toggle';
    toggleButton.id = 'novruz-toggle';
    toggleButton.innerHTML = '<i class="fas fa-fire"></i>';
    toggleButton.title = 'Novruz effektlərini aç/bağla';
    
    // Elementləri əlavə et
    header.appendChild(novruzTitle);
    header.appendChild(grassContainer);
    header.appendChild(fireContainer);
    header.appendChild(woodContainer);
    header.appendChild(semeniContainer);
    document.body.appendChild(toggleButton);
}

// Toggle düyməsinin işləməsi
function setupNovruzToggle() {
    const toggleButton = document.getElementById('novruz-toggle');
    
    if (!toggleButton) return;
    
    toggleButton.addEventListener('click', function() {
        const isActive = localStorage.getItem('novruzActive') === 'true';
        
        if (isActive) {
            // Deaktiv et
            hideNovruzElements();
            localStorage.setItem('novruzActive', 'false');
        } else {
            // Aktiv et
            showNovruzElements();
            localStorage.setItem('novruzActive', 'true');
        }
    });
}

// Local Storage-dən vəziyyəti yoxla
function checkNovruzState() {
    const isActive = localStorage.getItem('novruzActive');
    
    // İlk dəfə açılanda aktiv et
    if (isActive === null) {
        localStorage.setItem('novruzActive', 'true');
        showNovruzElements();
    } else if (isActive === 'false') {
        hideNovruzElements();
    } else {
        showNovruzElements();
    }
}

// Novruz elementlərini göstər
function showNovruzElements() {
    const elements = [
        'novruz-title',
        'grass-container',
        'fire-container',
        'wood-container',
        'semeni-container'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'block';
        }
    });
    
    // Toggle düyməsini yenilə
    const toggleButton = document.getElementById('novruz-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = '<i class="fas fa-fire"></i>';
        toggleButton.style.backgroundColor = '#FF6D00';
    }
}

// Novruz elementlərini gizlət
function hideNovruzElements() {
    const elements = [
        'novruz-title',
        'grass-container',
        'fire-container',
        'wood-container',
        'semeni-container'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });
    
    // Toggle düyməsini yenilə
    const toggleButton = document.getElementById('novruz-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = '<i class="fas fa-fire-alt"></i>';
        toggleButton.style.backgroundColor = '#555';
    }
} 