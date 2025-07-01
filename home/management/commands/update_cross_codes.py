import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from home.models import Mehsul

class Command(BaseCommand):
    help = "Məhsullar üçün cross reference kodlarını jsfilter.jp saytından çəkir və kodlar sahəsinə yazır"

    def handle(self, *args, **kwargs):
        for mehsul in Mehsul.objects.all():
            kodlar = []
            brend_kodlar = [k.strip() for k in mehsul.brend_kod.split('/') if k.strip()]
            for kod in brend_kodlar:
                url = f"https://jsfilter.jp/catalogue?search={kod}"
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, "html.parser")
                        # Cross reference kodlarını tapmaq üçün selector (sayt dəyişərsə, buranı dəyişmək lazımdır)
                        for tag in soup.find_all("td"):
                            text = tag.get_text(strip=True)
                            if text and text not in kodlar and text != kod:
                                kodlar.append(text)
                except Exception as e:
                    print(f"{kod} üçün xəta: {e}")
            if kodlar:
                mehsul.kodlar = " ".join(kodlar)
                mehsul.save()
                print(f"{mehsul.id} üçün kodlar yeniləndi.") 