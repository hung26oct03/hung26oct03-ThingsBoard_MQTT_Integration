import json
from utils.mqtt_device import DeviceMQTT
import time
import csv
import random

class DeviceSimulator:
    def __init__(self, csv_file_devices, tb_api, mqtt_host):
        self.mqtt_host = mqtt_host
        self.devices = []
        self.tb_api = tb_api
        self.device_credentials(csv_file_devices)
        
    def device_credentials(self, csv_file_devices):
        try:
            with open(csv_file_devices, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    device_name = row.get('name')
                    access_token = self.tb_api.get_device_credentials(device_name)
                    
                    if access_token:
                        device = DeviceMQTT(device_name, access_token, self.mqtt_host)
                        self.devices.append(device)
        except Exception as e:
            print(f"Lỗi simulator load CSV: {e}")
        
    def connect_all_devices(self):
        connected_count = 0
        for device in self.devices:
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
                    telemetry_data = {
                        'temperature': round(random.uniform(20.0, 35.0), 2),
                        'heart_rate': round(random.uniform(60.0, 160.0), 2)
                    }
                    device.publish_telemetry(telemetry_data)
                print(f"\nLần {round_num} OKE")
                
                if round_num < num_rounds:
                    time.sleep(interval)
        except KeyboardInterrupt:
            pass
        
    def disconnect_all(self):
        for device in self.devices:
            device.disconnect()
        
        print('\nĐã ngắt kết nối tất cả devices')