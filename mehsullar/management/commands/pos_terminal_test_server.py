import socket
import threading
import json
import time
import random
import logging
from django.core.management.base import BaseCommand

# Logging konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('pos_terminal_server')

class POSTerminalEmulator:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = []
        
    def start(self):
        """Server-i başlat"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Socket-i yenidən istifadəyə imkan ver
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            logger.info(f"POS Terminal emulyatoru başladıldı - {self.host}:{self.port}")
            
            # Yeni müştəri bağlantılarını qəbul etmək üçün döngə
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"Yeni bağlantı - {address[0]}:{address[1]}")
                    
                    # Hər bir müştəri üçün ayrı thread başladırıq
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.clients.append((client_socket, address, client_thread))
                except Exception as e:
                    if self.is_running:
                        logger.error(f"Əlaqə qəbul edilərkən xəta: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Server başladılarkən xəta: {str(e)}")
        finally:
            self.stop()
    
    def stop(self):
        """Server-i dayandır"""
        self.is_running = False
        
        # Bütün müştəri bağlantılarını bağla
        for client_socket, _, _ in self.clients:
            try:
                client_socket.close()
            except:
                pass
        
        # Server socket-i bağla
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            
        logger.info("POS Terminal emulyatoru dayandırıldı")
    
    def handle_client(self, client_socket, address):
        """Müştəri bağlantısını idarə et"""
        try:
            # Müştəridən məlumatları al
            data = client_socket.recv(1024).decode()
            logger.info(f"{address[0]}:{address[1]} - Alınan məlumat: {data}")
            
            # JSON format yoxlaması və məlumatların təhlili
            try:
                request = json.loads(data)
                method = request.get('method')
                
                # Ödəniş metodu
                if method == 'payment':
                    # Terminal ödənişini simulyasiya et
                    response = self.simulate_payment(request)
                # Status yoxlaması
                elif method == 'status':
                    response = {
                        'success': True,
                        'status': 'online',
                        'message': 'Terminal aktivdir'
                    }
                # Digər əməliyyatlar
                else:
                    response = {
                        'success': False,
                        'error': 'Tanınmayan metod'
                    }
                
                # Cavabı müştəriyə göndər
                client_socket.sendall(json.dumps(response).encode())
                logger.info(f"{address[0]}:{address[1]} - Göndərilən cavab: {json.dumps(response)}")
            except json.JSONDecodeError:
                logger.error(f"{address[0]}:{address[1]} - Yanlış JSON formatı: {data}")
                error_response = {
                    'success': False,
                    'error': 'Yanlış məlumat formatı. JSON formatında olmalıdır.'
                }
                client_socket.sendall(json.dumps(error_response).encode())
                
        except Exception as e:
            logger.error(f"{address[0]}:{address[1]} - Müştəri ilə əlaqədə xəta: {str(e)}")
        finally:
            # Bağlantını bağla
            try:
                client_socket.close()
                logger.info(f"{address[0]}:{address[1]} - Bağlantı bağlandı")
            except:
                pass
    
    def simulate_payment(self, request):
        """POS terminal ödənişini simulyasiya et"""
        # Ödəniş məlumatlarını al
        amount = request.get('amount', 0)
        card_number = request.get('card_number')
        
        logger.info(f"Ödəniş simulyasiyası: {amount} AZN, Kart: {card_number}")
        
        # Ödəniş prosesini simulyasiya etmək üçün gözlə
        time.sleep(2)
        
        # 90% ehtimalla uğurlu ödəniş, 10% ehtimalla xəta
        if random.random() < 0.9:
            # Uğurlu ödəniş
            transaction_id = f"TX-{int(time.time())}-{random.randint(1000, 9999)}"
            return {
                'success': True,
                'transaction_id': transaction_id,
                'amount': amount,
                'message': 'Ödəniş uğurla tamamlandı'
            }
        else:
            # Xəta simulyasiyası
            error_codes = [
                "CARD_DECLINED",
                "INSUFFICIENT_FUNDS",
                "COMMUNICATION_ERROR",
                "TRANSACTION_TIMEOUT"
            ]
            error_code = random.choice(error_codes)
            return {
                'success': False,
                'error': error_code,
                'message': f"Ödəniş xətası: {error_code}"
            }


class Command(BaseCommand):
    help = 'POS Terminal emulator serverini başladır'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default='0.0.0.0', help='Server host ünvanı')
        parser.add_argument('--port', type=int, default=8080, help='Server portu')
        
    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        
        self.stdout.write(self.style.SUCCESS(f'POS Terminal emulyatoru başladılır - {host}:{port}'))
        
        # POS Terminal emulyatorunu başlat
        server = POSTerminalEmulator(host, port)
        try:
            server.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Server dayandırıldı (Keyboard Interrupt)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Server xətası: {str(e)}'))
        finally:
            server.stop() 