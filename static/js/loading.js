document.addEventListener("DOMContentLoaded", function () {
    const loadingConfig = {
        linksWithLoading: [
            "https://as-avto.com/main/",
            "https://as-avto.com/orders/",
            "https://as-avto.com/products/",
            "https://as-avto.com/about/",
            "https://as-avto.com/cart/",
            "https://as-avto.com/istifadeciler/profile/",
            "https://as-avto.com/istifadeciler/password_change/",
        ],
        loadingDuration: 1500,
        containerStyles: {
            backgroundColor: "rgba(10, 20, 50, 0.95)",
            zIndex: "9999"
        },
        logoConfig: {
            src: "/static/img/favicon.png",
            width: "120px",
            height: "120px"
        }
    };

    function initializeLoadingAnimation() {
        const allLinks = document.querySelectorAll("a");
        allLinks.forEach(link => {
            if (loadingConfig.linksWithLoading.includes(link.href)) {
                link.addEventListener("click", handleLinkClick);
            }
        });
    }

    function handleLinkClick(e) {
        e.preventDefault();
        showLoadingAnimation();
        setTimeout(() => {
            window.location.href = this.href;
        }, loadingConfig.loadingDuration);
    }

    function showLoadingAnimation() {
        // Remove existing loader
        const existingLoader = document.getElementById("loading-container");
        if (existingLoader) existingLoader.remove();

        // Create loading container
        const loadingContainer = document.createElement("div");
        loadingContainer.id = "loading-container";
        Object.assign(loadingContainer.style, {
            position: "fixed",
            top: "0",
            left: "0",
            width: "100vw",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            ...loadingConfig.containerStyles
        });

        // Create logo
        const logo = document.createElement("img");
        logo.src = loadingConfig.logoConfig.src;
        logo.alt = "Company Logo";
        Object.assign(logo.style, {
            width: loadingConfig.logoConfig.width,
            height: loadingConfig.logoConfig.height,
            marginBottom: "30px",
            animation: "fadeInLogo 1s ease-in-out",
            objectFit: "contain"
        });

        // Create spinner
        const spinner = document.createElement("div");
        spinner.style.cssText = `
            width: 70px;
            height: 70px;
            border: 7px solid rgba(255, 255, 255, 0.2);
            border-top: 7px solid #ffffff;
            border-radius: 50%;
            animation: spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        `;

        // Additional loading text
        const loadingText = document.createElement("p");
        loadingText.textContent = "Yüklənir...";
        loadingText.style.cssText = `
            color: white;
            marginTop: 20px;
            fontWeight: bold;
            animation: fadeIn 0.5s ease-in-out;
        `;

        // Assemble components
        loadingContainer.appendChild(logo);
        loadingContainer.appendChild(spinner);
        loadingContainer.appendChild(loadingText);
        document.body.appendChild(loadingContainer);
    }

    // Animations and styles
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

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        #loading-container {
            animation: fadeIn 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);

    // Initialize the loading animation
    initializeLoadingAnimation();
});