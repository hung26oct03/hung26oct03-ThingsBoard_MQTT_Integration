import requests
import csv
import json
import logging
logger = logging.getLogger(__name__)

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
    
    def get_all_device_profiles(self, json_file):
        try:
            url = f'{self.host}/api/deviceProfileInfos'
            params = {'pageSize': 1000, 'page': 0}
            res = requests.get(url, params=params, headers=self.get_header())
            
            res.raise_for_status() 
            devices = res.json().get('data', [])
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, ensure_ascii=False, indent=4)
                
            print('Lưu file device profile OK')   
            
        except Exception as e:
            print('Lỗi tại hàm lấy danh sách device profile: ', e)
            return
        
    def get_device_by_name(self, device_name):
        try:
            all_devices = self.get_all_devices()
            
            for device in all_devices:
                if device['name'] == device_name:
                    return device
            
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi tìm device {device_name}: {e}")
            return None
        
    def get_id_device_profile(self, name_device_profile, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                device_profiles = json.load(f)
            
            for profile in device_profiles:
                if profile.get('name') == name_device_profile:
                    profile_id = profile.get('id', {}).get('id')
                    print(f"Check: Tìm thấy device profile '{name_device_profile}': {profile_id}")
                    return profile_id
             
            return None
                
        except Exception as e:
            print(f"Lỗi tại hàm get_id_device_profile: {e}")
            return None
        
    def import_csv_bulk(self, csv_file, json_file):
        devices = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                devices.append(row)
                
        created_devices = []
        url = f'{self.host}/api/device'
        print('Check url: ', url)
        
        try:
            for idx, device_data in enumerate(devices, 1):
                device_profile_name = device_data.get('device_profile', 'default')
                device_profile_id = self.get_id_device_profile(device_profile_name, json_file)
                
                if not device_profile_id:
                    logger.warning(f"Not found device profile: {device_profile_name} for {device_data['name']}")  
                    continue
                
                payload = {
                    'name': device_data['name'],
                    'label': device_data.get('label', ''),
                    'deviceProfileId': {
                        'id': device_profile_id,
                        'entityType': 'DEVICE_PROFILE'
                    }
                }
                
                print(f'Check payload: {payload}')
                
                res = requests.post(url, json=payload, headers=self.get_header())
                
                if res.status_code == 400 or res.status_code == 409:
                    existing_device = self.get_device_by_name(device_data['name'])
                    
                    if existing_device:
                        created_devices.append(existing_device)
                        print(f"Check cũ: [{idx}/{len(devices)}] {device_data['name']} (đã tồn tại)")
                    else:
                        logger.warning(f"Không thể lấy thông tin device: {device_data['name']}")
                    
                    continue
                
                res.raise_for_status()
                
                device = res.json()
                created_devices.append(device)
                print(f"Check mới: [{idx}/{len(devices)}] {device_data['name']}")
                
            return created_devices
            
        except Exception as e:
            print('Lỗi tại hàm import csv: ', e)
            return created_devices
        
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
        
    def get_all_devices(self):
        url = f"{self.host}/api/tenant/devices"
        params = {'pageSize': 1000, 'page': 0}
        
        res = requests.get(url, params=params, headers=self.get_header())
        
        if res.status_code == 200:
            devices = res.json().get('data', [])
        
            return devices
        return []
    
    def get_token_of_device(self, device_id):
        url = f'{self.host}/api/device/{device_id}/credentials'
        res = requests.get(url, headers=self.get_header())
        
        if res.status_code == 200:
            credentials = res.json()
            return credentials.get('credentialsId')
        
        return None
    
    def retrieve_all_tokens(self, csv_file):
        csv_device_names = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_device_names.append(row['name'])
        
        print(f"Tìm thấy {len(csv_device_names)} devices trong CSV")
        
        all_devices = self.get_all_devices()
        
        if not all_devices:
            print('Check: Không có device nào trên ThingsBoard')
            return []
        
        matched_devices = [de for de in all_devices if de['name'] in csv_device_names]
        
        devices_tokens = []
        
        for idx, de in enumerate(matched_devices, 1):
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
            else:
                logger.warning(f"Không lấy được token cho device: {de_name}")
                
        print(f'Đã lấy {len(devices_tokens)} tokens')
        return devices_tokens       