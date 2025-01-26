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
    loadingContainer.style.background = "linear-gradient(120deg, #0d1b3e, #1a346f, #274c90)";
    loadingContainer.style.display = "flex";
    loadingContainer.style.flexDirection = "column";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";
    loadingContainer.style.overflow = "hidden";

    const backgroundCircles = document.createElement("div");
    backgroundCircles.className = "background-circles";
    loadingContainer.appendChild(backgroundCircles);

    const loadingText = document.createElement("div");
    loadingText.style.fontSize = "26px";
    loadingText.style.fontWeight = "bold";
    loadingText.style.color = "#ffffff";
    loadingText.style.marginBottom = "20px";
    loadingText.style.animation = "textGlow 1.5s ease-in-out infinite";
    loadingText.innerHTML = `Yüklənir<span id="dots">...</span>`;

    const spinner = document.createElement("div");
    spinner.className = "spinner";
    spinner.style.width = "60px";
    spinner.style.height = "60px";
    spinner.style.border = "6px solid rgba(255, 255, 255, 0.2)";
    spinner.style.borderTop = "6px solid #ffffff";
    spinner.style.borderRadius = "50%";
    spinner.style.animation = "spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite";

    const glowEffect = document.createElement("div");
    glowEffect.className = "glow";
    glowEffect.style.width = "100px";
    glowEffect.style.height = "100px";
    glowEffect.style.border = "2px solid rgba(255, 255, 255, 0.3)";
    glowEffect.style.borderRadius = "50%";
    glowEffect.style.position = "absolute";
    glowEffect.style.animation = "pulse 2s infinite";

    loadingContainer.appendChild(loadingText);
    loadingContainer.appendChild(glowEffect);
    loadingContainer.appendChild(spinner);
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
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.3); opacity: 1; }
    }

    @keyframes textGlow {
        0%, 100% { text-shadow: 0 0 5px #ffffff, 0 0 10px #ff99cc, 0 0 20px #ff99cc; }
        50% { text-shadow: 0 0 10px #ffffff, 0 0 20px #ff66aa, 0 0 40px #ff66aa; }
    }

    .background-circles::before,
    .background-circles::after {
        content: "";
        position: absolute;
        width: 200px;
        height: 200px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: moveCircles 5s linear infinite;
    }

    .background-circles::before {
        top: 20%;
        left: 10%;
    }

    .background-circles::after {
        bottom: 20%;
        right: 10%;
        animation-delay: 2.5s;
    }

    @keyframes moveCircles {
        0% { transform: translate(0, 0); }
        50% { transform: translate(30px, -30px); }
        100% { transform: translate(0, 0); }
    }
`;
document.head.appendChild(style);
