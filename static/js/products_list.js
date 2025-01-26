document.addEventListener("DOMContentLoaded", function () {
    // Saat funksiyası
    const currentTimeElement = document.getElementById("current-time");
    function updateCurrentTime() {
        if (currentTimeElement) {
            const now = new Date();
            const hours = now.getHours().toString().padStart(2, "0");
            const minutes = now.getMinutes().toString().padStart(2, "0");
            const seconds = now.getSeconds().toString().padStart(2, "0");
            currentTimeElement.innerHTML = `
                <span class="time-unit">${hours}</span>:
                <span class="time-unit">${minutes}</span>:
                <span class="time-unit">${seconds}</span>
            `;
        }
    }
    setInterval(updateCurrentTime, 1000);

    // İş saatlarını yoxlama funksiyası
    function checkWorkingHours() {
        const now = new Date();
        const currentHour = now.getHours();
        const isWorkingHours = currentHour >= 9 && currentHour < 18;
        const workingHoursElement = document.querySelector(".working-hours p:first-child");
        if (workingHoursElement) {
            workingHoursElement.style.color = isWorkingHours ? "#4caf50" : "#ff5252";
            workingHoursElement.innerHTML = `İş vaxtımız: 09:00 - 18:00 
                <span class="status-badge" style="margin-left: 10px; font-size: 0.9em;">
                    ${isWorkingHours ? "🟢 Açıqdır" : "🔴 Bağlıdır"}
                </span>`;
        }
    }
    setInterval(checkWorkingHours, 60000);
    updateCurrentTime();
    checkWorkingHours();

    // Səbətə əlavə funksiyası
    const cartLinks = document.querySelectorAll(".cart-icon");
    cartLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault(); // Default davranışı dayandırırıq
            const icon = this.querySelector("i");

            // İkona yükləmə animasiyası əlavə edirik
            icon.classList.add("fa-spinner", "fa-spin");
            icon.classList.remove("fa-shopping-cart");

            // 2 saniyəlik yükləmə
            setTimeout(() => {
                // Yükləmə bitdikdən sonra ikon dəyişir və mesaj göstərilir
                icon.classList.remove("fa-spinner", "fa-spin");
                icon.classList.add("fa-check-circle");
                this.style.color = "#4caf50"; // Yaşıl rəng

                // Mesaj göstərilir
                const message = document.createElement("span");
                message.textContent = " Məhsul səbətə əlavə olundu!";
                message.style.color = "#4caf50";
                message.style.marginLeft = "10px";
                this.parentElement.appendChild(message);

                // 2 saniyə sonra mesaj və ikon default vəziyyətə qayıdır
                setTimeout(() => {
                    message.remove();
                    icon.classList.remove("fa-check-circle");
                    icon.classList.add("fa-shopping-cart");
                    this.style.color = ""; // Default rəng
                }, 2000);
            }, 2000);
        });
    });

    // Səbət sayını yeniləmək üçün AJAX funksiyası
    function updateCartCount() {
        fetch("/get_cart_count/") // Backend-dən səbət sayını alırıq
            .then(response => response.json())
            .then(data => {
                document.getElementById("cart-count").textContent = data.count;
            })
            .catch(error => console.error("Səbət sayını yeniləmə xətası:", error));
    }
    updateCartCount(); // Səhifə yüklənəndə səbət sayını yenilə

    // Axtarış düyməsi üçün yükləmə animasiyası
    const searchForm = document.querySelector("form");
    const searchButton = document.getElementById("search-button");
    const buttonText = searchButton.querySelector(".button-text");
    const spinner = searchButton.querySelector(".spinner");
    searchForm.addEventListener("submit", function (e) {
        e.preventDefault(); // Default form davranışını dayandırırıq
        searchButton.classList.add("loading");
        buttonText.style.opacity = "0.5";
        spinner.style.display = "inline-block";

        // 2 saniyəlik yükləmə
        setTimeout(() => {
            searchButton.classList.remove("loading");
            buttonText.style.opacity = "1";
            spinner.style.display = "none";
            this.submit(); // Formanı göndəririk
        }, 2000);
    });
});
