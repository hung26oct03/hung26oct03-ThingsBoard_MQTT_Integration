import json
from utils.mqtt_devices import DeviceMQTT
import time

class DeviceSimulator:
    def __init__(self, token_file, thingsboard_host):
        self.host = thingsboard_host
        self.devices = []
        self.load_tokens(token_file)
    
    def load_tokens(self, token_file):
        try:
            with open(token_file, 'r') as f:
                tokens = json.load(f)
            
            for device_name, access_token in tokens.items():
                device = DeviceMQTT(device_name, access_token, self.host)
                self.devices.append(device)
                
            return True      
        except FileNotFoundError:
            print("Lỗi đọc file: {token_file}")
            return False
        except Exception as e:
            print("Lỗi đọc tokens: {e}")
            return False
        
    def connect_all_devices(self):
        connected_count = 0
        for device in self.devices:
            # print('Check device: ', device)
            if device.connect():
                connected_count += 1
                
        print(f'Check: Đã kết nối {connected_count}/{len(self.devices)} devices')
        return connected_count > 0
    
    def send_attributes(self):
        for i, device in enumerate(self.devices):
            attributes = {
                'device_number': i,
                'description': f'Device số {i}'
            }
            device.publish_attributes(attributes)
        
        print('Check: Đã gửi attributes')
    
    def simulator_telemetry_publishing(self, num_rounds=5, interval=5):
        try:
            for round_num in range(1, num_rounds + 1):
                for device in self.devices:
                    telemetry_data = device.generate_telemetry_data()
                    device.publish_telemetry(telemetry_data)
                print(f"\Lần {round_num} OKE")
                
                if round_num < num_rounds:
                    time.sleep(interval)
        except KeyboardInterrupt:
            pass
        
    def disconnect_all(self):
        for device in self.devices:
            device.disconnect()
        
        print('\nĐã ngắt kết nối tất cả devices')