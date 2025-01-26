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

    const loadingContainer = document.createElement("div");
    loadingContainer.id = "loading-container";
    loadingContainer.style.position = "fixed";
    loadingContainer.style.top = "0";
    loadingContainer.style.left = "0";
    loadingContainer.style.width = "100vw";
    loadingContainer.style.height = "100vh";
    loadingContainer.style.background = "linear-gradient(135deg, #0f172a, #1e293b)"; // Tünd rəng keçidləri
    loadingContainer.style.display = "flex";
    loadingContainer.style.flexDirection = "column";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    const loadingText = document.createElement("div");
    loadingText.style.fontSize = "28px";
    loadingText.style.fontWeight = "bold";
    loadingText.style.color = "#ffffff";
    loadingText.style.marginBottom = "20px";
    loadingText.style.letterSpacing = "1px";
    loadingText.innerHTML = `<span id="loading-title">Yüklənir</span><span id="dots">...</span>`;

    const spinnerContainer = document.createElement("div");
    spinnerContainer.style.display = "flex";
    spinnerContainer.style.justifyContent = "center";
    spinnerContainer.style.alignItems = "center";
    spinnerContainer.style.gap = "15px";

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("div");
        dot.className = "spinner-dot";
        dot.style.width = "15px";
        dot.style.height = "15px";
        dot.style.backgroundColor = "#ffffff";
        dot.style.borderRadius = "50%";
        dot.style.animation = `dotBounce 1.2s cubic-bezier(0.4, 0, 0.6, 1) infinite`;
        dot.style.animationDelay = `${i * 0.2}s`;
        spinnerContainer.appendChild(dot);
    }

    loadingContainer.appendChild(loadingText);
    loadingContainer.appendChild(spinnerContainer);
    document.body.appendChild(loadingContainer);

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
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes dotBounce {
        0%, 80%, 100% {
            transform: scale(0);
        }
        40% {
            transform: scale(1);
        }
    }

    #loading-container {
        animation: fadeIn 0.5s ease-in-out;
    }

    #loading-title {
        font-family: 'Roboto', sans-serif;
        text-transform: uppercase;
    }

    .spinner-dot {
        animation-timing-function: cubic-bezier(0.68, -0.55, 0.27, 1.55); /* Daha səliqəli animasiya */
    }
`;
document.head.appendChild(style);
