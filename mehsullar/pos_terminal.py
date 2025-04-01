import socket
import logging
import time
import json
import traceback
from decimal import Decimal

logger = logging.getLogger(__name__)

class POSTerminalIntegration:
    """
    POS terminal ilə əlaqə qurmaq üçün servis sinfi.
    Bu sinif WiFi/IP üzərindən terminallarla əlaqə qurur.
    """
    def __init__(self, ip_address, port=8080, timeout=30, debug=False):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False
        self.debug = debug
        
        if debug:
            # Debug rejimində logger-in səviyyəsini artır
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            
        logger.info(f"POSTerminalIntegration yaradıldı: {ip_address}:{port}, debug={debug}")
        
    def connect(self):
        """Terminal ilə əlaqə qurur"""
        try:
            logger.info(f"Terminal ilə bağlantı qurulmağa çalışılır: {self.ip_address}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            logger.debug(f"Socket yaradıldı, qoşulma cəhdi edilir...")
            self.socket.connect((self.ip_address, self.port))
            
            self.connected = True
            logger.info(f"POS terminala qoşuldu: {self.ip_address}:{self.port}")
            return True
        except socket.timeout:
            logger.error(f"POS terminala qoşulma zamanı timeout! Timeout={self.timeout} saniyə. Terminal cavab vermir.")
            self.connected = False
            return False
        except socket.error as e:
            logger.error(f"Socket xətası: {e}")
            if self.debug:
                logger.debug(f"Stack trace: {traceback.format_exc()}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"POS terminala qoşulma xətası: {e}")
            if self.debug:
                logger.debug(f"Stack trace: {traceback.format_exc()}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Terminal ilə əlaqəni kəsir"""
        if self.socket:
            try:
                self.socket.close()
                logger.info(f"POS terminal ilə əlaqə kəsildi: {self.ip_address}:{self.port}")
            except Exception as e:
                logger.error(f"POS terminaldan ayrılma xətası: {e}")
                if self.debug:
                    logger.debug(f"Stack trace: {traceback.format_exc()}")
            finally:
                self.socket = None
                self.connected = False
    
    def send_command(self, command):
        """Terminala əmr göndərir və cavabı gözləyir"""
        if not self.connected:
            logger.info("Terminal bağlı, avtomatik qoşulma sınayır...")
            if not self.connect():
                logger.error("Terminal ilə əlaqə qurula bilmədi")
                return None
        
        try:
            logger.info(f"Terminala əmr göndərilir: {command}")
            self.socket.sendall(command.encode())
            
            logger.debug("Terminaldan cavab gözlənilir...")
            response = self.socket.recv(1024).decode().strip()
            
            logger.info(f"Terminaldan cavab alındı: {response}")
            return response
        except socket.timeout:
            logger.error(f"Əmrə cavab gözlənilirkən timeout! Timeout={self.timeout} saniyə")
            self.connected = False
            return None
        except Exception as e:
            logger.error(f"Əmr göndərilməsi xətası: {e}")
            if self.debug:
                logger.debug(f"Stack trace: {traceback.format_exc()}")
            self.connected = False
            return None
    
    def process_payment(self, amount, reference_no=None, details=None):
        """
        Ödəniş əməliyyatını başladır
        
        Parametrlər:
        - amount: Ödəniş məbləği (Decimal)
        - reference_no: Əməliyyat istinad nömrəsi (optional)
        - details: Çekdə göstəriləcək satış detalları (dictionary)
        
        Geri qaytarır:
        - (success, transaction_id, message) tupli
        """
        if isinstance(amount, Decimal):
            amount = float(amount)
        
        # Məbləği 100-ə vurub tam ədədə çeviririk (qəpiklər üçün)
        amount_int = int(amount * 100)
        
        # Yeni əməliyyat istinad nömrəsi yaradaq (əgər verilməyibsə)
        if not reference_no:
            reference_no = f"TR{int(time.time())}"
        
        # Ödəniş əmrini formatlaşdır
        command = f"PAYMENT:{amount_int}:{reference_no}"
        
        logger.info(f"Ödəmə prosesi başladılır: {amount} AZN, istinad: {reference_no}")
        response = self.send_command(command)
        
        if not response:
            logger.error("Terminal ilə əlaqə zamanı xəta baş verdi, ödəmə edilə bilmədi")
            return False, None, "Terminal ilə əlaqə zamanı xəta baş verdi"
        
        # Nümunə cavab: SUCCESS:TX123456:Approved
        # və ya: ERROR:Declined-Insufficient funds
        parts = response.split(":", 2)
        
        if parts[0] == "SUCCESS":
            transaction_id = parts[1] if len(parts) > 1 else None
            message = parts[2] if len(parts) > 2 else "Ödəniş uğurla tamamlandı"
            
            logger.info(f"Ödəmə uğurludur! Əməliyyat ID: {transaction_id}")
            
            # Ödəniş uğurlu olduqda çek çıxar
            print_result = self.print_receipt(amount, transaction_id, reference_no, details)
            if print_result:
                logger.info("Çek uğurla çap edildi")
            else:
                logger.warning("Çek çapında problem yarandı")
            
            return True, transaction_id, message
        else:
            error_message = parts[1] if len(parts) > 1 else "Naməlum xəta"
            logger.error(f"Ödəmə xətası: {error_message}")
            return False, None, error_message
    
    def print_receipt(self, amount, transaction_id, reference_no, details=None):
        """
        Terminaldan çek çıxarır
        
        Parametrlər:
        - amount: Ödəniş məbləği
        - transaction_id: Əməliyyat ID-si
        - reference_no: İstinad nömrəsi
        - details: Çekdə göstəriləcək satış detalları (dictionary)
        """
        try:
            logger.info(f"Çek çıxarılır, əməliyyat ID: {transaction_id}")
            
            # Əgər detallar varsa, onları JSON formatında göndər
            if details:
                logger.debug(f"Detallı çek çıxarılır, detallar: {details}")
                details_json = json.dumps(details)
                command = f"PRINT_RECEIPT_WITH_DETAILS:{transaction_id}:{details_json}"
            else:
                # Sadə çek çıxarma əmri
                logger.debug("Sadə çek çıxarılır")
                command = f"PRINT_RECEIPT:{transaction_id}"
            
            response = self.send_command(command)
            if response and response.startswith("SUCCESS"):
                logger.info(f"Çek uğurla çıxarıldı: {transaction_id}")
                return True
            else:
                logger.warning(f"Çek çıxarma problemi: {response}")
                # Əgər detallı çek alınmadısa, sadə çek sınayaq
                if details and "PRINT_RECEIPT_WITH_DETAILS" in command:
                    logger.info("Sadə çek çıxarmağa çalışılır...")
                    return self.print_receipt(amount, transaction_id, reference_no)
                return False
        except Exception as e:
            logger.error(f"Çek çıxarma xətası: {e}")
            if self.debug:
                logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False
    
    def check_status(self):
        """Terminal statusunu yoxlayır"""
        logger.info("Terminal statusu yoxlanılır")
        response = self.send_command("STATUS")
        
        if not response:
            logger.error("Terminal ilə əlaqə yoxdur, status sorğusuna cavab alınmadı")
            return False, "Terminal ilə əlaqə yoxdur"
        
        parts = response.split(":", 1)
        if parts[0] == "READY":
            logger.info("Terminal hazırdır")
            # Uğurlu olarsa terminal məlumatlarını əldə et
            terminal_info = self.get_terminal_info()
            return True, f"Terminal işləyir. {terminal_info}"
        else:
            logger.warning(f"Terminal hazır deyil: {parts[1] if len(parts) > 1 else 'Naməlum səbəb'}")
            return False, parts[1] if len(parts) > 1 else "Terminal hazır deyil"
    
    def get_terminal_info(self):
        """Terminal haqqında ətraflı məlumat alır"""
        logger.info("Terminal məlumatları istənilir")
        response = self.send_command("INFO")
        
        if not response:
            logger.warning("Terminal məlumatları alına bilmədi")
            return "Məlumat əldə edilə bilmədi"
        
        # INFO:Model=XYZ:Version=1.0:SerialNo=123456:State=READY
        parts = response.split(":")
        if parts[0] == "INFO" and len(parts) > 1:
            # Məlumatları format et
            info_parts = parts[1:]
            info_str = ", ".join(info_parts)
            logger.info(f"Terminal məlumatları: {info_str}")
            return info_str
        else:
            logger.warning("Terminal məlumatları tanınmadı")
            return "Məlumat formatı tanınmadı"
    
    def cancel_transaction(self, transaction_id):
        """
        Son əməliyyatı ləğv edir
        
        Parametrlər:
        - transaction_id: Ləğv ediləcək əməliyyatın ID-si
        
        Geri qaytarır:
        - (success, message) tupli
        """
        logger.info(f"Əməliyyat ləğv edilir, əməliyyat ID: {transaction_id}")
        command = f"CANCEL:{transaction_id}"
        response = self.send_command(command)
        
        if not response:
            logger.error("Terminal ilə əlaqə zamanı xəta baş verdi, ləğv əməliyyatı uğursuz oldu")
            return False, "Terminal ilə əlaqə zamanı xəta baş verdi"
        
        parts = response.split(":", 1)
        if parts[0] == "SUCCESS":
            logger.info("Əməliyyat uğurla ləğv edildi")
            # Ləğv prosesi uğurlu olduqda ləğv çeki çıxar
            print_result = self.print_void_receipt(transaction_id)
            if print_result:
                logger.info("Ləğv çeki uğurla çap edildi")
            else:
                logger.warning("Ləğv çeki çapında problem yarandı")
            
            return True, parts[1] if len(parts) > 1 else "Əməliyyat uğurla ləğv edildi"
        else:
            logger.error(f"Əməliyyat ləğv edilə bilmədi: {parts[1] if len(parts) > 1 else 'Naməlum səbəb'}")
            return False, parts[1] if len(parts) > 1 else "Əməliyyat ləğv edilə bilmədi"
            
    def print_void_receipt(self, transaction_id):
        """
        Ləğv əməliyyatı üçün çek çıxarır
        
        Parametrlər:
        - transaction_id: Ləğv edilən əməliyyatın ID-si
        """
        try:
            logger.info(f"Ləğv çeki çıxarılır, əməliyyat ID: {transaction_id}")
            # Ləğv çeki çıxarmaq üçün əmr formatı
            command = f"PRINT_VOID:{transaction_id}"
            
            response = self.send_command(command)
            if response and response.startswith("SUCCESS"):
                logger.info(f"Ləğv çeki uğurla çıxarıldı: {transaction_id}")
                return True
            else:
                logger.warning(f"Ləğv çeki çıxarma problemi: {response}")
                return False
        except Exception as e:
            logger.error(f"Ləğv çeki çıxarma xətası: {e}")
            if self.debug:
                logger.debug(f"Stack trace: {traceback.format_exc()}")
            return False

class DummyPOSTerminal(POSTerminalIntegration):
    """
    POS terminal simulyasiyası.
    Əsl terminal olmadığı halda debug və test üçün istifadə edilir.
    """
    def __init__(self, ip_address="127.0.0.1", port=8080, timeout=30, debug=True):
        super().__init__(ip_address, port, timeout, debug)
        logger.info("DummyPOSTerminal yaradıldı - simulyasiya rejimi aktiv")
        self.connected = True  # Simulyasiya terminalı hər zaman bağlıdır
        
    def connect(self):
        """Terminal ilə əlaqə simulyasiyası"""
        logger.info("Dummy terminal ilə bağlantı simulyasiyası")
        self.connected = True
        return True
        
    def disconnect(self):
        """Terminal ilə əlaqəni kəsmə simulyasiyası"""
        logger.info("Dummy terminal ilə bağlantı kəsildi (simulyasiya)")
        self.connected = False
        
    def send_command(self, command):
        """Terminala əmr göndərmə simulyasiyası"""
        logger.info(f"Dummy terminalına əmr göndərilir: {command}")
        
        # Əmrə görə müxtəlif cavablar qaytaraq
        if command.startswith("STATUS"):
            return "READY:Terminal hazırdır (simulyasiya)"
        elif command.startswith("INFO"):
            return "INFO:Model=SimulationPOS:Version=1.0:SerialNo=SIM123456:State=READY:Mode=TEST"
        elif command.startswith("PAYMENT"):
            parts = command.split(":")
            amount = int(parts[1]) / 100 if len(parts) > 1 else 0
            ref_no = parts[2] if len(parts) > 2 else "unknown"
            tx_id = f"TX{int(time.time())}"
            
            logger.info(f"Simulyasiya ödəmə: {amount} AZN, istinad: {ref_no}, TX ID: {tx_id}")
            return f"SUCCESS:{tx_id}:Ödəmə uğurla simulyasiya edildi"
        elif command.startswith("PRINT_RECEIPT"):
            return "SUCCESS:Çek çıxarıldı (simulyasiya)"
        elif command.startswith("CANCEL"):
            return "SUCCESS:Əməliyyat ləğv edildi (simulyasiya)"
        elif command.startswith("PRINT_VOID"):
            return "SUCCESS:Ləğv çeki çıxarıldı (simulyasiya)"
        else:
            return "ERROR:Naməlum əmr"


def get_terminal(ip_address, port=8080, timeout=30, debug=False, dummy=False):
    """
    IP adresinə görə terminal obyekti qaytarır.
    Əgər IP localhost və ya 127.0.0.1-dirsə və ya dummy=True olarsa, 
    dummy terminal qaytarılır.
    """
    if dummy or ip_address in ["127.0.0.1", "localhost"]:
        logger.info(f"Dummy terminal yaradılır (simulyasiya rejimi)")
        return DummyPOSTerminal(ip_address, port, timeout, debug)
    else:
        return POSTerminalIntegration(ip_address, port, timeout, debug) 