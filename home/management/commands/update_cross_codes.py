import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from home.models import Mehsul
import time

class Command(BaseCommand):
    help = "Məhsullar üçün cross reference kodlarını jsfilter.jp saytından çəkir və kodlar sahəsinə yazır"

    def handle(self, *args, **kwargs):
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
                search_url = f"https://jsfilter.jp/catalogue?search={kod}"
                try:
                    resp = requests.get(search_url, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        # 1. Birbaşa məhsul səhifəsinə yönləndirilirsə, cross reference kodlarını tap
                        cross_found = False
                        cross_section = soup.find(string=lambda s: s and "Cross reference" in s)
                        if cross_section:
                            table = cross_section.find_parent("table")
                            if table:
                                for row in table.find_all("tr"):
                                    cols = row.find_all("td")
                                    if len(cols) >= 2:
                                        code = cols[1].get_text(strip=True)
                                        if code and code != kod:
                                            kodlar.add(code)
                                cross_found = True
                        # 2. Siyahı çıxırsa, bütün məhsul linklərini tap və hər birinə daxil ol
                        if not cross_found:
                            product_links = []
                            for a in soup.find_all("a", href=True):
                                href = a["href"]
                                if "/catalogue/filter/" in href and href not in product_links:
                                    product_links.append(href)
                            if product_links:
                                print(f"    {len(product_links)} məhsul tapıldı, hər birinə baxılır...")
                            for link in product_links:
                                product_url = "https://jsfilter.jp" + link
                                print(f"    Məhsul səhifəsinə daxil olunur: {product_url}")
                                prod_resp = requests.get(product_url, timeout=10)
                                if prod_resp.status_code == 200:
                                    prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
                                    cross_section = prod_soup.find(string=lambda s: s and "Cross reference" in s)
                                    if cross_section:
                                        table = cross_section.find_parent("table")
                                        if table:
                                            for row in table.find_all("tr"):
                                                cols = row.find_all("td")
                                                if len(cols) >= 2:
                                                    code = cols[1].get_text(strip=True)
                                                    if code and code != kod:
                                                        kodlar.add(code)
                                time.sleep(1.2)
                        if not kodlar:
                            print(f"    Cross reference kod tapılmadı.")
                    else:
                        print(f"    Sayt cavab vermədi: {resp.status_code}")
                except Exception as e:
                    print(f"    {kod} üçün xəta: {e}")
                time.sleep(1.5)  # Hər koddan sonra 1.5 saniyə gözlə
            if kodlar:
                mehsul.kodlar = " ".join(sorted(kodlar))
                mehsul.save()
                print(f"  -> {mehsul.id} üçün kodlar yeniləndi: {kodlar}")
            else:
                print(f"  -> {mehsul.id} üçün yeni kod tapılmadı.") 