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
    loadingContainer.style.backgroundColor = "rgba(10, 20, 50, 0.9)"; // Tünd göy rəng
    loadingContainer.style.display = "flex";
    loadingContainer.style.flexDirection = "column";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    const logo = document.createElement("img");
    logo.src = "static/img/favicon.png"; // Burada logonuzun yolunu əlavə edin
    logo.alt = "Logo";
    logo.style.width = "100px";
    logo.style.height = "100px";
    logo.style.marginBottom = "20px";
    logo.style.animation = "fadeInLogo 1s ease-in-out";

    const spinner = document.createElement("div");
    spinner.className = "spinner";
    spinner.style.width = "60px";
    spinner.style.height = "60px";
    spinner.style.border = "6px solid rgba(255, 255, 255, 0.2)";
    spinner.style.borderTop = "6px solid #ffffff";
    spinner.style.borderRadius = "50%";
    spinner.style.animation = "spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite";

    loadingContainer.appendChild(logo);
    loadingContainer.appendChild(spinner);
    document.body.appendChild(loadingContainer);
}

const style = document.createElement("style");
style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes fadeInLogo {
        from { opacity: 0; transform: scale(0.8); }
        to { opacity: 1; transform: scale(1); }
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
