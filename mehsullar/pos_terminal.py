import socket
import logging
import time
from decimal import Decimal

logger = logging.getLogger(__name__)

class POSTerminalIntegration:
    """
    POS terminal ilə əlaqə qurmaq üçün servis sinfi.
    Bu sinif WiFi/IP üzərindən terminallarla əlaqə qurur.
    """
    def __init__(self, ip_address, port=8080, timeout=30):
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.connected = False
        
    def connect(self):
        """Terminal ilə əlaqə qurur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.ip_address, self.port))
            self.connected = True
            logger.info(f"POS terminala qoşuldu: {self.ip_address}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"POS terminala qoşulma xətası: {e}")
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
            finally:
                self.socket = None
                self.connected = False
    
    def send_command(self, command):
        """Terminala əmr göndərir və cavabı gözləyir"""
        if not self.connected:
            if not self.connect():
                return None
                
        try:
            self.socket.sendall(command.encode())
            response = self.socket.recv(1024).decode().strip()
            logger.debug(f"Terminaldan cavab alındı: {response}")
            return response
        except Exception as e:
            logger.error(f"Əmr göndərilməsi xətası: {e}")
            self.connected = False
            return None
    
    def process_payment(self, amount, reference_no=None):
        """
        Ödəniş əməliyyatını başladır
        
        Parametrlər:
        - amount: Ödəniş məbləği (Decimal)
        - reference_no: Əməliyyat istinad nömrəsi (optional)
        
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
        
        response = self.send_command(command)
        if not response:
            return False, None, "Terminal ilə əlaqə zamanı xəta baş verdi"
        
        # Nümunə cavab: SUCCESS:TX123456:Approved
        # və ya: ERROR:Declined-Insufficient funds
        parts = response.split(":", 2)
        
        if parts[0] == "SUCCESS":
            transaction_id = parts[1] if len(parts) > 1 else None
            message = parts[2] if len(parts) > 2 else "Ödəniş uğurla tamamlandı"
            return True, transaction_id, message
        else:
            error_message = parts[1] if len(parts) > 1 else "Naməlum xəta"
            return False, None, error_message
    
    def check_status(self):
        """Terminal statusunu yoxlayır"""
        response = self.send_command("STATUS")
        if not response:
            return False, "Terminal ilə əlaqə yoxdur"
        
        parts = response.split(":", 1)
        if parts[0] == "READY":
            return True, "Terminal işləyir"
        else:
            return False, parts[1] if len(parts) > 1 else "Terminal hazır deyil"
    
    def cancel_transaction(self, transaction_id):
        """
        Son əməliyyatı ləğv edir
        
        Parametrlər:
        - transaction_id: Ləğv ediləcək əməliyyatın ID-si
        
        Geri qaytarır:
        - (success, message) tupli
        """
        command = f"CANCEL:{transaction_id}"
        response = self.send_command(command)
        
        if not response:
            return False, "Terminal ilə əlaqə zamanı xəta baş verdi"
        
        parts = response.split(":", 1)
        if parts[0] == "SUCCESS":
            return True, parts[1] if len(parts) > 1 else "Əməliyyat uğurla ləğv edildi"
        else:
            return False, parts[1] if len(parts) > 1 else "Əməliyyat ləğv edilə bilmədi" 