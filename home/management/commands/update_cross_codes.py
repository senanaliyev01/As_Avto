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
            kodlar = []
            if '/' in mehsul.brend_kod:
                brend_kodlar = [k.strip() for k in mehsul.brend_kod.split('/') if k.strip()]
            else:
                brend_kodlar = [mehsul.brend_kod.strip()]
            for kod in brend_kodlar:
                print(f"  Kod yoxlanır: {kod}")
                search_url = f"https://jsfilter.jp/catalogue?search={kod}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                try:
                    resp = requests.get(search_url, headers=headers, timeout=10, allow_redirects=True)
                    print("Gələn URL:", resp.url)
                    print("Status:", resp.status_code)
                    print("HTML başlanğıcı:", resp.text[:500])
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        # 1. Əgər birbaşa məhsul səhifəsinə yönləndirilibsə, cross reference bölməsini tap
                        cross_found = False
                        cross_section = soup.find(string=lambda s: s and "Cross reference" in s)
                        if cross_section:
                            # Cross reference başlığını tapdıqdan sonra, onun altındakı kodları yığ
                            table = cross_section.find_parent("table")
                            if table:
                                for row in table.find_all("tr"):
                                    cols = row.find_all("td")
                                    if len(cols) >= 2:
                                        code = cols[1].get_text(strip=True)
                                        if code and code not in kodlar and code != kod:
                                            kodlar.append(code)
                                cross_found = True
                        # 2. Əgər siyahı çıxıbsa, ilk məhsulun linkini tap və ora daxil ol
                        if not cross_found:
                            # Siyahıdakı ilk məhsulun linkini tap
                            first_link = soup.find("a", href=True, text=True)
                            if first_link and "/catalogue/filter/" in first_link["href"]:
                                product_url = "https://jsfilter.jp" + first_link["href"]
                                print(f"    Məhsul səhifəsinə daxil olunur: {product_url}")
                                prod_resp = requests.get(product_url, timeout=7)
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
                                                    if code and code not in kodlar and code != kod:
                                                        kodlar.append(code)
                        if not kodlar:
                            print(f"    Cross reference kod tapılmadı.")
                    else:
                        print(f"    Sayt cavab vermədi: {resp.status_code}")
                except Exception as e:
                    print(f"    {kod} üçün xəta: {e}")
                time.sleep(1.5)  # Hər koddan sonra 1.5 saniyə gözlə
            if kodlar:
                mehsul.kodlar = " ".join(kodlar)
                mehsul.save()
                print(f"  -> {mehsul.id} üçün kodlar yeniləndi: {kodlar}")
            else:
                print(f"  -> {mehsul.id} üçün yeni kod tapılmadı.") 