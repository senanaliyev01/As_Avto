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
                url = f"https://jsfilter.jp/catalogue?search={kod}"
                try:
                    resp = requests.get(url, timeout=7)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for tag in soup.find_all("td"):
                            text = tag.get_text(strip=True)
                            if text and text not in kodlar and text != kod:
                                kodlar.append(text)
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