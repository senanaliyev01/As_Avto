// HTML dosyasına uygun bir ID ilə bağlanılabilir. JS yalnız loading efektini düzenler.

// Sayfa yüklendiğinde dinamik bir "loading" animasyonu göstermek üçün JS kodları.

document.addEventListener("DOMContentLoaded", function () {
    // Loading animasiyasını yalnız təyin edilmiş linklər üçün tətbiq etmək
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
                }, 2000); // 2 saniyə sonra linkə yönləndirir
            });
        }
    });
});

function showLoadingAnimation() {
    // Var olan loading ekranını silmək (əgər mövcuddursa)
    const existingLoader = document.getElementById("loading-container");
    if (existingLoader) existingLoader.remove();

    // Yeni loading animasiyası yaratmaq
    const loadingContainer = document.createElement("div");
    loadingContainer.id = "loading-container";
    loadingContainer.style.position = "fixed";
    loadingContainer.style.top = "0";
    loadingContainer.style.left = "0";
    loadingContainer.style.width = "100vw";
    loadingContainer.style.height = "100vh";
    loadingContainer.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
    loadingContainer.style.display = "flex";
    loadingContainer.style.justifyContent = "center";
    loadingContainer.style.alignItems = "center";
    loadingContainer.style.zIndex = "9999";

    const loadingContent = document.createElement("div");
    loadingContent.style.textAlign = "center";
    loadingContent.style.color = "white";
    loadingContent.innerHTML = `
        <div style="font-size: 24px; margin-bottom: 20px;">Yüklənir<span id="dots">.</span></div>
        <div class="spinner" style="width: 50px; height: 50px; border: 5px solid rgba(255, 255, 255, 0.3); border-top: 5px solid white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
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
    }, 500); // Hər yarım saniyədə nöqtələri dəyişir
}

// CSS üçün dinamik spinner animasiyası əlavə edirik
const style = document.createElement("style");
style.innerHTML = `
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
