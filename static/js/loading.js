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
    const allLinks = document.querySelectorAll("a");
    allLinks.forEach(link => {
        if (linksWithLoading.includes(link.href)) {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                showLoadingAnimation();
                setTimeout(() => {
                    window.location.href = link.href;
                }, 1200);
            });
        }
    });
});

function showLoadingAnimation() {
    const existingLoader = document.getElementById("loading-container");
    if (existingLoader) existingLoader.remove();

    // Create main loading container
    const loadingContainer = document.createElement("div");
    loadingContainer.id = "loading-container";
    loadingContainer.style.position = "fixed";
    loadingContainer.style.top = "0";
    loadingContainer.style.left = "0";
    loadingContainer.style.width = "100vw";
    loadingContainer.style.height = "100vh";
    loadingContainer.style.backgroundColor = "rgba(10, 20, 50, 0.95)";
    loadingContainer.style.display = "flex";
    loadingContainer.style.flexDirection = "column";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";
    loadingContainer.style.backdropFilter = "blur(10px)";

    // Animated logo or brand placeholder
    const brandLogo = document.createElement("div");
    brandLogo.style.width = "120px";
    brandLogo.style.height = "120px";
    brandLogo.style.backgroundColor = "#ffffff";
    brandLogo.style.borderRadius = "50%";
    brandLogo.style.display = "flex";
    brandLogo.style.justifyContent = "center";
    brandLogo.style.alignItems = "center";
    brandLogo.style.marginBottom = "30px";
    brandLogo.style.animation = "pulse 1.5s infinite";
    
    const logoText = document.createElement("span");
    logoText.textContent = "AS";
    logoText.style.fontSize = "42px";
    logoText.style.fontWeight = "bold";
    logoText.style.color = "rgba(10, 20, 50, 0.8)";
    brandLogo.appendChild(logoText);

    // Loading text
    const loadingText = document.createElement("div");
    loadingText.style.fontSize = "26px";
    loadingText.style.fontWeight = "bold";
    loadingText.style.color = "#ffffff";
    loadingText.style.marginBottom = "20px";
    loadingText.innerHTML = `Yüklənir<span id="dots">...</span>`;

    // Progress bar
    const progressBar = document.createElement("div");
    progressBar.style.width = "300px";
    progressBar.style.height = "6px";
    progressBar.style.backgroundColor = "rgba(255,255,255,0.2)";
    progressBar.style.borderRadius = "3px";
    progressBar.style.marginTop = "20px";
    progressBar.style.overflow = "hidden";

    const progressIndicator = document.createElement("div");
    progressIndicator.style.width = "0%";
    progressIndicator.style.height = "100%";
    progressIndicator.style.backgroundColor = "#ffffff";
    progressIndicator.style.transition = "width 1.2s ease-in-out";
    progressBar.appendChild(progressIndicator);

    // Spinner
    const spinner = document.createElement("div");
    spinner.className = "spinner";
    spinner.style.width = "60px";
    spinner.style.height = "60px";
    spinner.style.border = "6px solid rgba(255, 255, 255, 0.2)";
    spinner.style.borderTop = "6px solid #ffffff";
    spinner.style.borderRadius = "50%";
    spinner.style.animation = "spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite";

    // Assemble components
    loadingContainer.appendChild(brandLogo);
    loadingContainer.appendChild(loadingText);
    loadingContainer.appendChild(spinner);
    loadingContainer.appendChild(progressBar);
    document.body.appendChild(loadingContainer);

    // Animate progress bar and dots
    animateProgress(progressIndicator);
    animateDots();
}

function animateProgress(progressIndicator) {
    setTimeout(() => {
        progressIndicator.style.width = "30%";
    }, 400);
    setTimeout(() => {
        progressIndicator.style.width = "60%";
    }, 800);
    setTimeout(() => {
        progressIndicator.style.width = "90%";
    }, 1100);
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
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    #loading-container {
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);