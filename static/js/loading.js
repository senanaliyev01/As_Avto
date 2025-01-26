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
                }, 1500); // Daha uzun yükləmə animasiyası üçün vaxt artırıldı
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
    loadingContainer.style.background = "linear-gradient(135deg, #1d3557, #457b9d)"; // Gradient rəng
    loadingContainer.style.display = "flex";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    const loadingContent = document.createElement("div");
    loadingContent.style.textAlign = "center";
    loadingContent.style.color = "#ffffff";
    loadingContent.innerHTML = `
        <div style="font-size: 26px; font-weight: bold; margin-bottom: 20px; animation: fadeInText 1s infinite;">
            Yüklənir<span id="dots">...</span>
        </div>
        <div class="spinner" style="width: 60px; height: 60px; border: 6px solid rgba(255, 255, 255, 0.2); border-top: 6px solid #ffffff; border-radius: 50%; animation: spin 1.2s ease-in-out infinite;"></div>
        <div style="margin-top: 20px; font-size: 14px; animation: pulseText 1.5s infinite;">
            Zəhmət olmasa gözləyin
        </div>
    `;

    loadingContainer.appendChild(loadingContent);
    document.body.appendChild(loadingContainer);

    animateDots();
}

function animateDots() {
    const dots = document.getElementById("dots");
    let count = 1;
    setInterval(() => {
        dots.textContent = ".".repeat(count);
        count = count < 3 ? count + 1 : 1;
    }, 300); // Daha yüngül və axıcı nöqtə animasiyası
}

const style = document.createElement("style");
style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes fadeInText {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    @keyframes pulseText {
        0%, 100% { color: #ffffff; }
        50% { color: #a8dadc; }
    }

    #loading-container {
        animation: fadeIn 0.6s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);
