from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from django.core.management.base import BaseCommand
from home.models import Mehsul
import re
import time

class Command(BaseCommand):
    help = "Məhsullar üçün cross reference kodlarını Google və əsas ehtiyat hissəsi saytlarından avtomatik toplayır"

    def handle(self, *args, **kwargs):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)

        products = Mehsul.objects.all()
        for idx, mehsul in enumerate(products, 1):
            print(f"{idx}/{products.count()} - Yoxlanır: {mehsul.adi} (ID: {mehsul.id}) | brend_kod: {mehsul.brend_kod}")
            kodlar = set()
            if '/' in mehsul.brend_kod:
                brend_kodlar = [k.strip() for k in mehsul.brend_kod.split('/') if k.strip()]
            else:
                brend_kodlar = [mehsul.brend_kod.strip()]
            for kod in brend_kodlar:
                print(f"  Kod yoxlanır: {kod}")
                query = f"{kod} cross reference"
                driver.get(f"https://www.google.com/search?q={query}")
                time.sleep(2)
                links = driver.find_elements(By.CSS_SELECTOR, 'div.yuRUbf > a')
                for link in links[:5]:
                    href = link.get_attribute('href')
                    print(f"    Nəticə yoxlanır: {href}")
                    try:
                        driver.get(href)
                        time.sleep(2)
                        # Səhifədəki bütün mətnləri topla
                        page_text = driver.find_element(By.TAG_NAME, 'body').text
                        # 10 simvoldan uzun, hərf və rəqəm olan kodları tap
                        found_codes = set(re.findall(r'\\b[A-Z0-9\\-]{6,}\\b', page_text, re.I))
                        for fc in found_codes:
                            if fc.lower() != kod.lower():
                                kodlar.add(fc)
                    except Exception as e:
                        print(f"      Xəta: {e}")
            if kodlar:
                mehsul.kodlar = ' '.join(kodlar)
                mehsul.save()
                print(f"  -> {mehsul.id} üçün kodlar yeniləndi: {kodlar}")
            else:
                print(f"  -> {mehsul.id} üçün yeni kod tapılmadı.")
        driver.quit() 