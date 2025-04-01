# POS Terminal İnteqrasiyası və Test Server

## POS Terminal İnteqrasiyası Haqqında

Bu layihə WiFi/IP üzərindən POS terminal inteqrasiyasını təmin edir. Beləliklə, satışlar zamanı POS terminal ilə birbaşa əlaqə quraraq ödənişlərin qəbul edilməsi və idarə edilməsi mümkün olacaq.

## Test Server İstifadəsi

Əsl POS terminal olmadığı halda, geliştirici və test mühitində test üçün hazırlanmış `pos_terminal_test_server.py` istifadə edilə bilər. Bu server, POS terminalın davranışını simulasiya edərək, eyni protokol və əlaqə üsullarından istifadə edir.

### Server-i Başlatmaq

Test serveri başlatmaq üçün aşağıdakı əmri çalışdırın:

```bash
python manage.py pos_terminal_test_server
```

Varsayılan olaraq, server `0.0.0.0:8080` adresində dinləməyə başlayacaq. Bu parametrləri dəyişdirmək üçün əlavə parametrlər istifadə edə bilərsiniz:

```bash
python manage.py pos_terminal_test_server --host=127.0.0.1 --port=9000
```

### Server İşləyərkən

Server işləyərkən, admin panelindən POS terminal əlavə etmək və satışlar yaratmaq mümkündür:

1. Admin panelindən "POS Terminallar" bölməsinə keçin
2. Yeni terminal əlavə edin (Test server üçün IP: `127.0.0.1`, Port: `8080`)
3. "Satışlar" bölməsindən yeni satış yaradın
4. "POS Terminal" sütunundan test terminalı seçin
5. Ödəniş metodu olaraq "POS Terminal" seçin
6. Satışı yaradın və saxlayın
7. Satışlar siyahısından satışı seçin və "POS Terminal ilə ödəniş et" əməliyyatını çalışdırın

### Test Server Xüsusiyyətləri

Test server aşağıdakı xüsusiyyətlərə malikdir:

- 90% ehtimalla uğurlu ödəniş qaytarır
- 10% ehtimalla müxtəlif xəta mesajları qaytarır
- Hər uğurlu ödəniş üçün unikal əməliyyat ID-si yaradır
- Bütün əməliyyatlar üçün loq yazır

## Əsl POS Terminal İnteqrasiyası

Əsl POS terminal ilə inteqrasiya üçün, terminalın protokol və əlaqə üsullarına uyğun olaraq əlavə inteqrasiya işləri tələb oluna bilər. Bu halda, `POSTerminal` modelindəki `odenis_et` və `baglanti_yoxla` metodları uyğun şəkildə yenilənməlidir.

## Troubleshooting

1. "Terminalla bağlantı qurula bilmədi" xətası alınırsa:
   - Test serverin işlədiyindən əmin olun
   - Terminal IP və portun doğru olduğunu yoxlayın
   - Firewall tənzimləmələrini yoxlayın

2. Digər ödəniş xətaları:
   - Server loqlarını yoxlayın
   - Test server simulyasiyasında təsadüfi xəta mesajları ola bilər 