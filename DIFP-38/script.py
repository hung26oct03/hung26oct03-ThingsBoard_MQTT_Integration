from dotenv import load_dotenv
import os
import time
import json

from utils.thingsboard import ThingsBoard
from utils.simulator import DeviceSimulator

load_dotenv()

TB_HOST = os.getenv("THINGSBOARD_HOST")
TB_USER = os.getenv("THINGSBOARD_USERNAME")
TB_PASS = os.getenv("THINGSBOARD_PASSWORD")

csv_file_devices = 'devices.csv'
json_file_device_profiles = 'device_profiles.json'
json_file_tokken_mapping = 'token_mapping.json'
csv_file_mock_data = 'mock_data.csv'

def save_tokens_to_json(devices, filename='device_tokens.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(devices, f, indent=2, ensure_ascii=False)
    
    mapping = {de['device_name']: de['access_token'] for de in devices}
    with open(json_file_tokken_mapping, 'w') as f:
        json.dump(mapping, f, indent=2)

def run_main():
    try:
        api = ThingsBoard(TB_HOST, TB_USER, TB_PASS)
        
        api.get_all_device_profiles(json_file_device_profiles)
        created_devices = api.import_csv_bulk(csv_file_devices, json_file_device_profiles)
        
        if not created_devices:
            print('Lỗi ở bước tạo devices')
            return

        time.sleep(5)
        
        devices_tokens = api.retrieve_all_tokens(csv_file_devices)
        if not devices_tokens:
            print('Lỗi tại bước import csv')
            return
        
        save_tokens_to_json(devices=devices_tokens)
        
        mqtt_host = TB_HOST.replace('http://', '').replace('https://', '').split(':')[0]
        print('Check mqtt host: ', mqtt_host)
        
        simulator = DeviceSimulator(
            json_file_tokken_mapping, 
            mqtt_host,
            csv_file_devices,
            csv_file_mock_data
        )
        
        if not simulator.connect_all_devices():
            print('Lỗi, không device nào kết nối được')
            return
        
        simulator.send_attributes()
        
        num_rounds = 5
        interval = 5
        
        simulator.simulator_telemetry_publishing(num_rounds=num_rounds, interval=interval)
        simulator.disconnect_all()
        
    except Exception as e:
        print(f"Lỗi script: {e}")
        
if __name__ == '__main__':
    run_main()