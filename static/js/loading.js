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
                showLoadingAnimation(link.href);
            });
        }
    });
});

function showLoadingAnimation(targetUrl) {
    const existingLoader = document.getElementById("loading-container");
    if (existingLoader) existingLoader.remove();

    const loadingContainer = document.createElement("div");
    loadingContainer.id = "loading-container";
    loadingContainer.style.position = "fixed";
    loadingContainer.style.top = "0";
    loadingContainer.style.left = "0";
    loadingContainer.style.width = "100vw";
    loadingContainer.style.height = "100vh";
    loadingContainer.style.backgroundColor = "rgba(255,255,255,1)";
    loadingContainer.style.display = "flex";
    loadingContainer.style.flexDirection = "column";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    // Your logo image
    const brandLogo = document.createElement("img");
    brandLogo.src = "/path/to/your/logo.png"; // Replace with actual logo path
    brandLogo.style.maxWidth = "200px";
    brandLogo.style.marginBottom = "30px";

    // Loading text
    const loadingText = document.createElement("div");
    loadingText.style.fontSize = "22px";
    loadingText.style.fontWeight = "bold";
    loadingText.style.color = "#333";
    loadingText.style.marginBottom = "20px";
    loadingText.textContent = "Yüklənir...";

    // Progress bar
    const progressBar = document.createElement("div");
    progressBar.style.width = "300px";
    progressBar.style.height = "6px";
    progressBar.style.backgroundColor = "rgba(0,0,0,0.1)";
    progressBar.style.borderRadius = "3px";
    progressBar.style.overflow = "hidden";

    const progressIndicator = document.createElement("div");
    progressIndicator.style.width = "0%";
    progressIndicator.style.height = "100%";
    progressIndicator.style.backgroundColor = "#007bff";
    progressIndicator.style.transition = "width 3s linear";
    progressBar.appendChild(progressIndicator);

    loadingContainer.appendChild(brandLogo);
    loadingContainer.appendChild(loadingText);
    loadingContainer.appendChild(progressBar);
    document.body.appendChild(loadingContainer);

    // Animate progress bar
    progressIndicator.style.width = "100%";

    // Navigate after progress completes
    setTimeout(() => {
        const exitAnimation = document.createElement("style");
        exitAnimation.innerHTML = `
            @keyframes fadeOut {
                from { opacity: 1; transform: scale(1); }
                to { opacity: 0; transform: scale(1.1); }
            }
            #loading-container {
                animation: fadeOut 0.5s forwards;
            }
        `;
        document.head.appendChild(exitAnimation);

        setTimeout(() => {
            window.location.href = targetUrl;
        }, 500);
    }, 3000);
}

const style = document.createElement("style");
style.innerHTML = `
    body { margin: 0; overflow-x: hidden; }
`;
document.head.appendChild(style);