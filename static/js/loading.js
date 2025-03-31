document.addEventListener("DOMContentLoaded", function () {
    const CONFIG = {
        links: {
            loadingPaths: [
                "/main/",
                "/orders/",
                "/products/",
                "/about/",
                // "/cart/",
                "/istifadeciler/profile/",
                "/istifadeciler/password_change/",
                "/istifadeciler/register/",
                "/istifadeciler/login/",
                "/rent-a-car/",
                "/products-look-all/",
                "/reports/",
                "/new-products/",
            ],
            baseUrl: "https://as-avto.com"
        },
        loading: {
            duration: 1000,
            containerStyle: {
                background: "rgba(10, 20, 50, 0.95)",
                zIndex: 9999
            },
            logo: {
                src: "/static/img/favicon.png",
                width: 120,
                height: 120
            }
        }
    };

    class LoadingManager {
        constructor(config) {
            this.config = config;
            this.initializeEventListeners();
            this.createStylesheet();
        }

        initializeEventListeners() {
            document.querySelectorAll('a').forEach(link => {
                const fullUrl = `${this.config.links.baseUrl}${link.getAttribute('href')}`;
                if (this.config.links.loadingPaths.some(path => fullUrl.endsWith(path))) {
                    link.addEventListener('click', this.handleLinkClick.bind(this));
                }
            });
        }

        handleLinkClick(event) {
            event.preventDefault();
            this.showLoadingScreen(event.currentTarget.href);
        }

        showLoadingScreen(targetUrl) {
            this.removeExistingLoader();
            const loadingContainer = this.createLoadingContainer();
            const logo = this.createLogo();
            const spinner = this.createSpinner();
            const loadingText = this.createLoadingText();

            loadingContainer.append(logo, spinner, loadingText);
            document.body.appendChild(loadingContainer);

            setTimeout(() => {
                window.location.href = targetUrl;
            }, this.config.loading.duration);
        }

        removeExistingLoader() {
            const existingLoader = document.getElementById("loading-container");
            if (existingLoader) existingLoader.remove();
        }

        createLoadingContainer() {
            const container = document.createElement("div");
            container.id = "loading-container";
            Object.assign(container.style, {
                position: "fixed",
                top: 0,
                left: 0,
                width: "100vw",
                height: "100vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                ...this.config.loading.containerStyle
            });
            return container;
        }

        createLogo() {
            const logo = document.createElement("img");
            logo.src = this.config.loading.logo.src;
            logo.alt = "Company Logo";
            Object.assign(logo.style, {
                width: `${this.config.loading.logo.width}px`,
                height: `${this.config.loading.logo.height}px`,
                marginBottom: "30px",
                animation: "fadeInLogo 1s ease-in-out",
                objectFit: "contain"
            });
            return logo;
        }

        createSpinner() {
            const spinner = document.createElement("div");
            spinner.style.cssText = `
                width: 70px;
                height: 70px;
                border: 7px solid rgba(255, 255, 255, 0.2);
                border-top: 7px solid #ffffff;
                border-radius: 50%;
                animation: spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            `;
            return spinner;
        }

        createLoadingText() {
            const loadingText = document.createElement("p");
            loadingText.textContent = "";
            loadingText.style.cssText = `
                color: white;
                margin-top: 20px;
                font-weight: bold;
                animation: fadeIn 0.5s ease-in-out;
            `;
            return loadingText;
        }

        createStylesheet() {
            const style = document.createElement("style");
            style.textContent = `
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
        }
    }

    // Initialize the loading manager
    new LoadingManager(CONFIG);
});