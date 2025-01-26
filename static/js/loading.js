document.addEventListener("DOMContentLoaded", function () {
    const linksWithLoading = [
        "https://as-avto.com/main/",
        "https://as-avto.com/orders/",
        "https://as-avto.com/products/",
        "https://as-avto.com/about/",
        "https://as-avto.com/cart/",
        "https://as-avto.com/istifadeciler/profile/",
        "https://as-avto.com/istifadeciler/password_change/",
    ];

    const translations = {
        az: "Yüklənir...",
        en: "Loading...",
        ru: "Загрузка..."
    };

    function getLanguage() {
        return document.documentElement.lang || 'az';
    }

    function handlePageTransition(link) {
        return new Promise((resolve, reject) => {
            const controller = new AbortController();
            const maxLoadTime = 3000;
            const timeoutId = setTimeout(() => {
                controller.abort();
                reject(new Error('Page load timeout'));
            }, maxLoadTime);

            fetch(link.href, { 
                method: 'GET',
                signal: controller.signal 
            })
            .then(response => {
                clearTimeout(timeoutId);
                resolve(response);
            })
            .catch(error => {
                clearTimeout(timeoutId);
                reject(error);
            });
        });
    }

    let isTransitioning = false;
    const allLinks = document.querySelectorAll("a");

    allLinks.forEach(link => {
        if (linksWithLoading.includes(link.href)) {
            link.addEventListener("click", function (e) {
                if (isTransitioning) {
                    e.preventDefault();
                    return;
                }
                
                isTransitioning = true;
                e.preventDefault();
                showLoadingAnimation();
                
                handlePageTransition(link)
                    .then(() => {
                        window.location.href = link.href;
                    })
                    .catch(error => {
                        console.error("Səhifə yüklənməsində xəta:", error);
                        const loadingText = document.getElementById('loading-text');
                        if (loadingText) {
                            loadingText.textContent = "Xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin.";
                        }
                    });
                
                setTimeout(() => {
                    isTransitioning = false;
                }, 2000);
            });
        }
    });

    function showLoadingAnimation() {
        const existingLoader = document.getElementById("loading-container");
        if (existingLoader) existingLoader.remove();

        const loadingContainer = document.createElement("div");
        loadingContainer.id = "loading-container";
        loadingContainer.style.position = "fixed";
        loadingContainer.style.top = "0";
        loadingContainer.style.left = "0";
        loadingContainer.style.width = "100vw";
        loadingContainer.style.height = "100vh";
        loadingContainer.style.backgroundColor = "rgba(10, 20, 50, 0.9)";
        loadingContainer.style.display = "flex";
        loadingContainer.style.flexDirection = "column";
        loadingContainer.style.justifyContent = "center";
        loadingContainer.style.alignItems = "center";
        loadingContainer.style.zIndex = "9999";

        const loadingText = document.createElement("div");
        loadingText.id = "loading-text";
        loadingText.style.fontSize = "26px";
        loadingText.style.fontWeight = "bold";
        loadingText.style.color = "#ffffff";
        loadingText.style.marginBottom = "20px";
        loadingText.innerHTML = `${translations[getLanguage()]}<span id="dots">...</span>`;

        const progressBar = document.createElement("div");
        progressBar.style.width = "0%";
        progressBar.style.height = "4px";
        progressBar.style.backgroundColor = "#00ffff";
        progressBar.style.position = "absolute";
        progressBar.style.top = "0";
        progressBar.style.left = "0";
        progressBar.style.transition = "width 1.2s ease-in-out";

        const spinner = document.createElement("div");
        spinner.className = "spinner";
        spinner.style.width = "60px";
        spinner.style.height = "60px";
        spinner.style.border = "6px solid rgba(255, 255, 255, 0.2)";
        spinner.style.borderTop = "6px solid #ffffff";
        spinner.style.borderRadius = "50%";
        spinner.style.animation = "spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite";

        loadingContainer.appendChild(progressBar);
        loadingContainer.appendChild(loadingText);
        loadingContainer.appendChild(spinner);
        document.body.appendChild(loadingContainer);
        document.body.classList.add('transition-out');

        setTimeout(() => {
            progressBar.style.width = "100%";
        }, 100);

        animateDots();
    }

    function animateDots() {
        const dots = document.getElementById("dots");
        let count = 1;
        setInterval(() => {
            dots.textContent = ".".repeat(count);
            count = count < 3 ? count + 1 : 1;
        }, 400);
    }

    const style = document.createElement("style");
    style.innerHTML = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes pageTransition {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.95); }
            100% { opacity: 0; transform: scale(0.9); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        #loading-container {
            animation: fadeIn 0.5s ease-in-out;
        }
        body.transition-out {
            animation: pageTransition 0.5s forwards;
        }
    `;
    document.head.appendChild(style);
});