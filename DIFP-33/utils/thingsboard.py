import requests
import csv

class ThingsBoard:
    def __init__(self, host, username, password):
        self.host = host
        self.token = None
        self.login(username, password)
    
    def get_header(self):
        return {
            'Content-Type': 'application/json',
            'X-Authorization': f'Bearer {self.token}'
        }
        
    def import_csv_bulk(self, csv_file):
        devices = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                devices.append(row)
                
        created_devices = []
        url = f'{self.host}/api/device'
        print('Check url: ', url);
        
        try:
            for idx, device_data in enumerate(devices, 1):
                payload = {
                    'name': device_data['name'],
                    'label': device_data['label']
                }
                
                print(f'Check payload: {payload}')
                
                res = requests.post(url, json=payload, headers=self.get_header())
                
                res.raise_for_status() 
                
                device = res.json()
                created_devices.append(device)
                print(f"OK: [{idx}/{len(devices)}] {device_data['name']}")
                
            return created_devices        
        except Exception as e:
            print('Lỗi tại hàm import csv: ', e)
            return
        
    def login(self, username, password):
        url = f"{self.host}/api/auth/login"
        res = requests.post(url, json={
            'username': username,
            'password': password
        })
        
        if res.status_code == 200:
            self.token = res.json()['token']
            # print(f'Check token: ', res.json()['token'])
            print('Đăng nhập OK')
        else:
            raise Exception(f"Lỗi: {res.text}")
        
    def get_all_devices(self, filter_text=None):
        url = f"{self.host}/api/tenant/devices"
        params = {'pageSize': 1000, 'page': 0}
        
        res = requests.get(url, params=params, headers=self.get_header())
        
        if res.status_code == 200:
            devices = res.json().get('data', [])
            
            if filter_text:
                devices = [de for de in devices if de['name'].startswith(filter_text)]
            
            return devices
        return []
    
    def get_token_of_device(self, device_id):
        url = f'{self.host}/api/device/{device_id}/credentials'
        res = requests.get(url, headers=self.get_header())
        
        if res.status_code == 200:
            credentials = res.json()
            return credentials.get('credentialsId')
        
        return None
    
    def retrieve_all_tokens(self, filter_text=None):
        devices = self.get_all_devices(filter_text)
        
        if not devices:
            print('Không tìm thấy devices')
            return []
        
        devices_tokens = []
        
        for de in devices:
            de_id = de['id']['id']
            de_name = de['name']
            de_label = de['label']
            
            token = self.get_token_of_device(device_id=de_id)
            
            if token:
                devices_tokens.append({
                    'device_id': de_id,
                    'device_name': de_name,
                    'device_label': de_label,
                    'access_token': token
                })
                
        print(f'Đã lấy {len(devices_tokens)} tokens')
        return devices_tokens       