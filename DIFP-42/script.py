from dotenv import load_dotenv
import os
import time
import json
import csv

from utils.thingsboard import ThingsBoard
from utils.simulator import DeviceSimulator

load_dotenv()

TB_HOST = os.getenv("THINGSBOARD_HOST")
TB_USER = os.getenv("THINGSBOARD_USERNAME")
TB_PASS = os.getenv("THINGSBOARD_PASSWORD")

csv_file_tenant = 'tenants.csv'
csv_file_tenant_admin = 'tenants_admin.csv'
csv_file_customer = 'customers.csv'
csv_file_customer_user = 'customers_user.csv'
csv_file_devices = 'devices.csv'

json_file_tenant_profiles = 'tenant_profiles.json'

def get_first_row(file_path): # Test
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return next(reader)
    except StopIteration:
        return None
    
def run_main():
    try:
        # ========== System Admin ===========
        print('1. Đăng nhập với tài khoản System Admin')
        api_admin = ThingsBoard(TB_HOST, "nguyenthanhhung26102003@gmail.com", "26102003")
        
        # print('2. Thêm Tenant')
        # with open(csv_file_tenant, 'r', encoding='utf-8') as f:
        #     reader = csv.DictReader(f)
        #     for row in reader:
        #         api_admin.add_tenant(row)
                
        print('3. Tạo tài khoản Tenant Admin')
        with open(csv_file_tenant_admin, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                api_admin.add_tenant_admin(row)
                
        # ========== Tenant ===========
        print('1. Đăng nhập với tài khoản Tenant Admin')
        api_tenant_admin = ThingsBoard(TB_HOST, "nth0326zz@gmail.com", "26102003")
        
        # print('2. Thêm Customer')  
        # with open(csv_file_customer, 'r', encoding='utf-8') as f:
        #     reader = csv.DictReader(f)
        #     for row in reader:
        #         api_tenant_admin.add_customer(row)    
        
        print('3. Tạo tài khoản Customer User')
        with open(csv_file_customer_user, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                api_tenant_admin.add_customer_user(row)       
        
        print('4. Thêm device')
        with open(csv_file_devices, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = api_tenant_admin.upsert_device(row)    
                print('Check data add device: ', data)  

        mqtt_host = TB_HOST.replace('http://', '').replace('https://', '').split(':')[0]
        simulator = DeviceSimulator(csv_file_devices, api_tenant_admin, mqtt_host)
        if not simulator.connect_all_devices():
            print('Lỗi, không device nào kết nối được')
            return
        
        simulator.send_attributes()
        
        num_rounds = 3
        interval = 5
        
        simulator.simulator_telemetry_publishing(num_rounds=num_rounds, interval=interval)
        
        print('5. Gán device cho customer')
        first_customer_user = get_first_row(csv_file_customer_user)
        first_device = get_first_row(csv_file_devices)
        customer_title = first_customer_user.get('customer_title')
        device_name = first_device.get('name')
        
        print(f"Check: gán device [{device_name}] cho customer [{customer_title}]...")
        result = api_tenant_admin.assign_device_to_customer(customer_title, device_name)
        
        if result:
            print('Gán thành công')
        else:
            print("Lỗi gán device")
            
        print('6. Gán dashboard cho customer')
        dashboard_name = "Dashboard DIFP-42"
        api_tenant_admin.assign_dashboard_to_customer(customer_title, dashboard_name)
        
        print('7. Xóa device')
        api_tenant_admin.delete_device(device_name)
        
        simulator.disconnect_all()
        
    except FileNotFoundError:
        print(f'Lỗi đọc file: {csv_file_tenant}') 
    except Exception as e:
        print(f"Lỗi script: {e}")
        
if __name__ == '__main__':
    run_main()