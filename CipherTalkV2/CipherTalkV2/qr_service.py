import json
import qrcode
import socket
from PIL import Image
import os

class QRService:
    @staticmethod
    def get_local_ip():
        """Get the local IP address of this machine"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def generate_connection_data(username, public_key, port=9000):
        """Generate connection data as JSON string"""
        local_ip = QRService.get_local_ip()
        
        connection_data = {
            "type": "cipher_talk_connection",
            "version": "1.0",
            "username": username,
            "public_key": public_key,
            "ip": local_ip,
            "port": port
        }
        
        return json.dumps(connection_data)
    
    @staticmethod
    def generate_qr_code(connection_data, filename=None):
        """Generate QR code from connection data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(connection_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if filename:
            img.save(filename)
            print(f"QR code saved as: {filename}")
        
        return img
    
    @staticmethod
    def display_connection_code(connection_data):
        """Display connection data as text code"""
        print("\n" + "="*50)
        print("CONNECTION CODE")
        print("="*50)
        print(connection_data)
        print("="*50)
        print("Share this code with others to connect!")
        print("="*50 + "\n")
    
    @staticmethod
    def parse_connection_data(connection_data_str):
        """Parse connection data from JSON string"""
        try:
            data = json.loads(connection_data_str)
            if data.get("type") == "cipher_talk_connection":
                return data
            else:
                print("Invalid connection data format")
                return None
        except json.JSONDecodeError:
            print("Invalid JSON format in connection data")
            return None
        except Exception as e:
            print(f"Error parsing connection data: {e}")
            return None
    
    @staticmethod
    def generate_and_save_connection_info(username, public_key, port=9000, save_qr=True):
        """Generate both QR code and text code for connection"""
        connection_data = QRService.generate_connection_data(username, public_key, port)
        
        # Display text code
        QRService.display_connection_code(connection_data)
        
        # Generate and save QR code
        if save_qr:
            qr_dir = os.path.expanduser("~/cipher_talk/qr_codes")
            os.makedirs(qr_dir, exist_ok=True)
            
            qr_filename = os.path.join(qr_dir, f"{username}_connection_qr.png")
            QRService.generate_qr_code(connection_data, qr_filename)
        
        return connection_data 