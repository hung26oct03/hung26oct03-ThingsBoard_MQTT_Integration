import json
import csv
from utils.mqtt_devices import DeviceMQTT
import time

class DeviceSimulator:
    def __init__(self, token_file, thingsboard_host, device_csv_file, mock_data_file):
        self.host = thingsboard_host
        self.devices = []
        self.mock_data = {}
        self.mock_data_index = {}
        self.load_mock_data(mock_data_file)
        self.load_tokens(token_file, device_csv_file)
    
    def load_mock_data(self, mock_data_file):
        try:
            with open(mock_data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    metric_type = row['metric_type'].strip()
                    value = float(row['value'])
                    
                    if metric_type not in self.mock_data:
                        self.mock_data[metric_type] = []
                        self.mock_data_index[metric_type] = 0
                    
                    self.mock_data[metric_type].append(value)
            
            print(f"Check: Đã load mock data: {', '.join([f'{k}: {len(v)} values' for k, v in self.mock_data.items()])}")
            return True
        except Exception as e:
            print(f"Lỗi load mock data: {e}")
            return False
    
    def load_tokens(self, token_file, device_csv_file):
        try:
            device_metrics = {}
            with open(device_csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    device_metrics[row['name']] = row['metric_type'].strip()
            
            with open(token_file, 'r') as f:
                tokens = json.load(f)
            
            for device_name, access_token in tokens.items():
                metric_type = device_metrics.get(device_name)
                device = DeviceMQTT(device_name, access_token, self.host, metric_type)
                self.devices.append(device)
                
            return True      
        except FileNotFoundError as e:
            print(f"Lỗi đọc file: {e}")
            return False
        except Exception as e:
            print(f"Lỗi đọc tokens: {e}")
            return False
    
    def get_next_mock_value(self, metric_type):
        values = self.mock_data[metric_type]
        index = self.mock_data_index[metric_type]
        
        value = values[index]
        
        self.mock_data_index[metric_type] = (index + 1) % len(values)
        
        return value
        
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
                'description': f'Device số {i}',
                'metric_type': device.metric_type
            }
            # print('Check attribute: ', device)
            device.publish_attributes(attributes)
        
        print('Check: Đã gửi attributes')
        time.sleep(2)
    
    def simulator_telemetry_publishing(self, num_rounds=5, interval=5):
        try:
            for round_num in range(1, num_rounds + 1):
                print(f"\n=> Gửi lần {round_num}")
                for device in self.devices:
                    value = self.get_next_mock_value(device.metric_type)
                    
                    telemetry_data = {
                        device.metric_type: round(value, 2)
                    }
                    
                    device.publish_telemetry(telemetry_data)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nDừng simulator")
        
    def disconnect_all(self):
        for device in self.devices:
            device.disconnect()
        
        print('\nĐã ngắt kết nối tất cả devices')