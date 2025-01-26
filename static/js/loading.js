document.addEventListener("DOMContentLoaded", function () {
    const linksWithLoading = [
        "https://as-avto.com/main/",
        "https://as-avto.com/orders/",
        "https://as-avto.com/products/",
        "https://as-avto.com/about/",
        "https://as-avto.com/cart/",
        "https://as-avto.com/istifadeciler/profile/",
    ]; // Yalnız bu linklərdə animasiya göstəriləcək

    const allLinks = document.querySelectorAll("a");
    allLinks.forEach(link => {
        if (linksWithLoading.includes(link.href)) {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                showLoadingAnimation();
                setTimeout(() => {
                    window.location.href = link.href;
                }, 1000); // 1 saniyə sonra yönləndirir
            });
        }
    });
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
    loadingContainer.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
    loadingContainer.style.display = "flex";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    const loadingContent = document.createElement("div");
    loadingContent.style.textAlign = "center";
    loadingContent.style.color = "white";
    loadingContent.innerHTML = `
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 20px;">
            <span id="loading-text">Yüklənir</span>
            <span id="dots">...</span>
        </div>
        <div class="spinner"></div>
    `;

    loadingContainer.appendChild(loadingContent);
    document.body.appendChild(loadingContainer);

    animateDots();
}

// Nöqtələri animasiya etmək
function animateDots() {
    const dots = document.getElementById("dots");
    let count = 1;
    setInterval(() => {
        dots.textContent = ".".repeat(count);
        count = count < 3 ? count + 1 : 1;
    }, 500); // Hər 500 ms-də nöqtələri dəyişir
}

// CSS üçün professional spinner və animasiya
const style = document.createElement("style");
style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinner {
        width: 60px;
        height: 60px;
        border: 6px solid rgba(255, 255, 255, 0.3);
        border-top: 6px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.6);
    }
    #loading-container div {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
`;
document.head.appendChild(style);
