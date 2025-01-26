document.addEventListener('DOMContentLoaded', () => {
    // Bütün linkləri seç
    const links = document.querySelectorAll('a');
    
    // Loading konteyneri yaradılır
    const loadingContainer = document.createElement('div');
    loadingContainer.style.position = 'fixed';
    loadingContainer.style.top = '50%';
    loadingContainer.style.left = '50%';
    loadingContainer.style.transform = 'translate(-50%, -50%)';
    loadingContainer.style.zIndex = '9999';
    loadingContainer.style.display = 'none';
    loadingContainer.style.textAlign = 'center';
    
    // Yuklenir mətn elementi
    const loadingText = document.createElement('div');
    loadingText.style.fontSize = '24px';
    loadingText.style.fontWeight = 'bold';
    loadingText.style.marginBottom = '20px';
    
    // Spinner elementi
    const spinner = document.createElement('div');
    spinner.style.width = '60px';
    spinner.style.height = '60px';
    spinner.style.border = '5px solid #f3f3f3';
    spinner.style.borderTop = '5px solid #3498db';
    spinner.style.borderRadius = '50%';
    spinner.style.animation = 'spin 1s linear infinite';
    spinner.style.margin = '0 auto';
    
    // Animasiya üsulu
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes dots {
            0%, 20% { content: '.'; }
            33%, 53% { content: '..'; }
            66%, 86% { content: '...'; }
        }
    `;
    
    document.head.appendChild(style);
    
    loadingContainer.appendChild(loadingText);
    loadingContainer.appendChild(spinner);
    document.body.appendChild(loadingContainer);
    
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            let dots = 0;
            const dotsInterval = setInterval(() => {
                dots = (dots + 1) % 4;
                loadingText.textContent = 'Yuklenir' + '.'.repeat(dots);
            }, 500);
            
            loadingContainer.style.display = 'block';
            
            setTimeout(() => {
                clearInterval(dotsInterval);
                loadingContainer.style.display = 'none';
                window.location.href = link.href;
            }, 2000);
        });
    });
});