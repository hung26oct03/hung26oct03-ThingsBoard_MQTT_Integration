import requests
import csv
import json
import logging
from apis.endpoints import thingsboard_endpoint
logger = logging.getLogger(__name__)

class ThingsBoard:
    def __init__(self, host, username, password):
        self.host = host
        self.token = None
        self.login(username, password)
    
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Authorization': f'Bearer {self.token}'
        }
        
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
        
    # =============== SYS ADMIN ===============
    def get_id_tenant_by_title(self, value):
        url = f"{self.host}/api/tenants"
        params = {'pageSize': 10, 'page': 0, 'textSearch': value}
        try:
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            
            for tenant in data.get("data", []):
                if tenant.get("title") == value:
                    return tenant.get("id", {}).get("id")
            return None
        except Exception as e:
            print(f"Lỗi khi lấy id tenant: {e}")
            return None
        
    def get_id_tenant_profile(self, value):
        url = f"{self.host}/api/tenantProfiles"
        params = {'pageSize': 10, 'page': 0, 'textSearch': value}
        try:         
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            
            for profile in data.get("data", []):
                if profile.get("name") == value:
                    return profile.get("id", {}).get("id")
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy id tenant profile: {e}")
            return None
            
    def add_tenant(self, data):
        url = f"{self.host}/api/tenant"
        profile_name = data.get('tenant_profile')
        tenant_profile_id = self.get_id_tenant_profile(profile_name)

        try:
            payload = {
                "title": data.get('title'),
                "email": data.get('email'),
                "country": data.get('country'),
                "state": data.get('state'),
                "city": data.get('city'),
                "address": data.get('address'),
                "address2": data.get('address2') if data.get('address2') else "",
                "zip": data.get('zip'),
                "phone": data.get('phone'),
                "tenantProfileId": {
                    "id": tenant_profile_id,
                    "entityType": "TENANT_PROFILE"
                },
                "additionalInfo": {
                    "description": data.get('description')
                }
            }
            
            res = requests.post(url, json=payload, headers=self.get_headers())
            res.raise_for_status()
            
            print(f"Thêm tenant '{data.get('title')}' thành công")
            return res.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi thêm tenant: {e}")
            
    # def add_tenant_admin(self, data):
    #     print('Check data: ', data)
    #     tenant_name = data.get('tenant_title')
    #     tenant_id = self.get_id_tenant_by_title(tenant_name)
    #     print('Check tenant id: ', tenant_id)
    #     url = f"{self.host}/api/user"
        
    #     payload = {
    #         "tenantId": {
    #             "id": tenant_id,
    #             "entityType": "TENANT"
    #         },
    #         "email": data.get('email'),
    #         "authority": "TENANT_ADMIN",
    #         "firstName": data.get('firstName'),
    #         "lastName": data.get('lastName'),
    #         "additionalInfo": {}
    #     }
        
    #     try:
    #         res = requests.post(url, json=payload, headers=self.get_headers())
    #         res.raise_for_status()
            
    #         print(f" OK: Đã thêm Admin '{data.get('email')}' vào Tenant '{tenant_name}'")
    #         return res.json()
            
    #     except requests.exceptions.RequestException as e:
    #         error_msg = e.response.text if e.response else str(e)
    #         print(f" Lỗi khi thêm Admin {data.get('email')}: {error_msg}")
    #         return None
    
    def add_tenant_admin(self, data):
        url = f"{self.host}/api/user?sendActivationMail=false"
        
        tenant_id = self.get_id_tenant_by_title(data.get('tenant_title'))
        payload = {
            "tenantId": {"id": tenant_id, "entityType": "TENANT"},
            "email": data.get('email'),
            "authority": "TENANT_ADMIN",
            "firstName": data.get('firstName'),
            "lastName": data.get('lastName')
        }
        
        try:
            res = requests.post(url, json=payload, headers=self.get_headers())
            res.raise_for_status()
            user_data = res.json()
            user_id = user_data['id']['id']

            url_link = f"{self.host}/api/user/{user_id}/activationLink"
            res_link = requests.get(url_link, headers=self.get_headers())
            activation_link = res_link.text
            token = activation_link.split('activateToken=')[-1]

            url_activate = f"{self.host}/api/noauth/activate"
            activate_payload = {
                "activateToken": token,
                "password": data.get('password', '26102003')
            }
            res_pw = requests.post(url_activate, json=activate_payload)
            res_pw.raise_for_status()

            print(f" OK: Đã tạo Admin '{data.get('email')}' và gán mật khẩu thành công.")
            return user_data

        except Exception as e:
            print(f" Lỗi: {e}")
            return None

    #=============== TENANT ===============
    def get_device_credentials(self, device_name):
        device_id = self.get_id_device_by_name(device_name)     
        url = f"{self.host}/api/device/{device_id}/credentials"
        
        try:
            res = requests.get(url, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            access_token = data.get("credentialsId")
            
            if access_token:
                return access_token
            else:
                return None
                
        except Exception as e:
            print(f"Lỗi khi lấy Device access token: {e}")
            return None
        
    def get_my_tenant_id(self):
        try:
            user_url = f"{self.host}/api/auth/user"
            user_res = requests.get(user_url, headers=self.get_headers())
            user_res.raise_for_status()
            user_data = user_res.json()
            
            tenant_id = user_data.get("tenantId", {}).get("id")
            
            return tenant_id
        except Exception as e:
            print(f"Lỗi khi lấy thông tin tenant: {e}")
            return None
        
    def get_id_device_profile(self, value):
        url = f"{self.host}/api/deviceProfiles"
        params = {
            'pageSize': 100, 
            'page': 0, 
            'textSearch': value
        }
        
        try:
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            
            for profile in data.get("data", []):
                if profile.get("name") == value:
                    return profile.get("id", {}).get("id")
    
            return None       
        except Exception as e:
            print(f"Lỗi khi lấy id device profile: {e}")
            return None
        
    def get_id_device_by_name(self, device_name):
        url = f"{self.host}/api/tenant/devices"
        params = {
            'pageSize': 100, 
            'page': 0, 
            'textSearch': device_name
        }
        
        try:
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            
            for device in data.get("data", []):
                if device.get("name") == device_name:
                    return device.get("id", {}).get("id")
            
            return None
        except Exception as e:
            print(f"Lỗi khi lấy id device '{device_name}': {e}")
            return None
        
    def add_customer(self, data):
        url = f"{self.host}/api/customer"   
        tenant_id = self.get_my_tenant_id()
        
        try:
            payload = {
                "title": data.get('title'),
                "email": data.get('email'),
                "country": data.get('country'),
                "state": data.get('state'),
                "city": data.get('city'),
                "address": data.get('address'),
                "zip": data.get('zip'),
                "phone": data.get('phone'),
                "tenantId": {
                    "id": tenant_id,
                    "entityType": "TENANT"
                },
                "additionalInfo": {
                    "description": data.get('description', '')
                }
            }
            
            res = requests.post(url, json=payload, headers=self.get_headers())
            res.raise_for_status()
            print(f"Thêm customer '{data.get('title')}' thành công")
            return res.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Lỗi thêm customer: {e.response.text if e.response else e}")
            return None
        
    def upsert_device(self, device_data):
        device_name = device_data.get('name')
        existing_id = self.get_id_device_by_name(device_name)
        tenant_id = self.get_my_tenant_id()
        profile_id = self.get_id_device_profile(device_data.get('device_profile', 'default'))

        payload = {
            "name": device_name,
            "type": device_data.get('type', 'default'),
            "label": device_data.get('label', ''),
            "tenantId": {"id": tenant_id, "entityType": "TENANT"},
            "deviceProfileId": {"id": profile_id, "entityType": "DEVICE_PROFILE"},
            "additionalInfo": {"description": device_data.get('description', '')}
        }

        if existing_id:
            payload["id"] = {"id": existing_id, "entityType": "DEVICE"}
            action = "update"
        else:
            action = "create"

        try:
            res = requests.post(f"{self.host}/api/device", json=payload, headers=self.get_headers())
            res.raise_for_status()
            return res.json(), action
        except Exception as e:
            print(f" [X] Lỗi {action} {device_name}: {e}")
            return None, None
        
    def delete_device(self, device_name):
        device_id = self.get_id_device_by_name(device_name)
        
        if not device_id:
            return False

        url = f"{self.host}/api/device/{device_id}"
        
        try:
            res = requests.delete(url, headers=self.get_headers())
            res.raise_for_status()
            
            print(f" OK: Đã xóa thành công thiết bị '{device_name}' (id: {device_id})")
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = e.response.text if e.response else str(e)
            print(f" Lỗi khi xóa thiết bị {device_name}: {error_msg}")
            return False
        
    def assign_device_to_customer(self, customer_title, device_name):
        try:
            customer_id = self.get_id_customer_by_title(customer_title)
            device_id = self.get_id_device_by_name(device_name)
            url = f"{self.host}/api/customer/{customer_id}/device/{device_id}"
            
            res = requests.post(url, headers=self.get_headers())
            res.raise_for_status()

            print(f" OK: Đã gán thiết bị '{device_name}' cho customer '{customer_title}'")
            return res.json()

        except Exception as e:
            error_msg = e.response.text if hasattr(e, 'response') else str(e)
            print(f"Lỗi khi gán thiết bị: {error_msg}")
            return False
          
    #=============== CUSTOMER ===============    
    def get_id_customer_by_title(self, customer_title):
        url = f"{self.host}/api/tenant/customers"
        params = {
            "customerTitle": customer_title
        }

        try:
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            data = res.json()
            return data.get("id", {}).get("id")
        except Exception as e:
            print(f"Lỗi tìm customer id: {e}")
            return None
        
    #=============== CUSTOMER USER ===============
    # def add_customer_user(self, data):
    #     url = f"{self.host}/api/user?sendActivationMail=true"
    #     tenant_id = self.get_my_tenant_id()
    #     customer_id = self.get_id_customer_by_title(data.get('customer_title')) 
        
    #     try:
    #         payload = {
    #             "tenantId": {"id": tenant_id, "entityType": "TENANT"},
    #             "customerId": {"id": customer_id, "entityType": "CUSTOMER"},
    #             "email": data.get('email'),
    #             "authority": "CUSTOMER_USER",
    #             "firstName": data.get('firstName', ''),
    #             "lastName": data.get('lastName', ''),
    #             "additionalInfo": {}
    #         }
            
    #         res = requests.post(url, json=payload, headers=self.get_headers())
    #         res.raise_for_status()
    #         print(f"Thêm customer user '{data.get('email')}' thành công")
    #         return res.json()    
                
    #     except requests.exceptions.RequestException as e:
    #         print(f"Lỗi thêm customer user: {e.response.text if e.response else e}")
    #         return None     

    def add_customer_user(self, data):
        url = f"{self.host}/api/user?sendActivationMail=false"
        tenant_id = self.get_my_tenant_id()
        customer_id = self.get_id_customer_by_title(data.get('customer_title')) 
        
        try:
            payload = {
                "tenantId": {"id": tenant_id, "entityType": "TENANT"},
                "customerId": {"id": customer_id, "entityType": "CUSTOMER"},
                "email": data.get('email'),
                "authority": "CUSTOMER_USER",
                "firstName": data.get('firstName', ''),
                "lastName": data.get('lastName', ''),
                "additionalInfo": {}
            }
            
            res = requests.post(url, json=payload, headers=self.get_headers())
            res.raise_for_status()
            user_data = res.json()
            user_id = user_data['id']['id']
            
            url_get_link = f"{self.host}/api/user/{user_id}/activationLink"
            res_link = requests.get(url_get_link, headers=self.get_headers())
            activation_link = res_link.text
            
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(activation_link)
            token = urlparse.parse_qs(parsed.query)['activateToken'][0]

            url_activate = f"{self.host}/api/noauth/activate"
            payload_activate = {
                "activateToken": token,
                "password": data.get('password', '26102003')
            }
            
            res_pw = requests.post(url_activate, json=payload_activate)
            res_pw.raise_for_status()

            print(f"Thành công: Đã tạo Customer User '{data.get('email')}' và đặt mật khẩu cứng.")
            return user_data    
                
        except requests.exceptions.RequestException as e:
            error_msg = e.response.text if e.response else str(e)
            print(f"Lỗi khi xử lý Customer User: {error_msg}")
            return None

        
    def assign_dashboard_to_customer(self, customer_title, dashboard_title):
        customer_id = self.get_id_customer_by_title(customer_title)
        dashboard_id = self.get_id_dashboard_by_title(dashboard_title)
        url = f"{self.host}/api/customer/{customer_id}/dashboard/{dashboard_id}"
        
        try:
            res = requests.post(url, headers=self.get_headers())
            res.raise_for_status()
            print(f" OK: Đã gán dashboard '{dashboard_title}' cho customer '{customer_title}'")
            return res.json()
        except Exception as e:
            print(f"Lỗi khi gán dashboard: {e}")
            return None
    
    #=============== DASHBOARD ===============
    def get_id_dashboard_by_title(self, title):
        url = f"{self.host}/api/tenant/dashboards"
        params = {'pageSize': 100, 'page': 0, 'textSearch': title}
        try:
            res = requests.get(url, params=params, headers=self.get_headers())
            res.raise_for_status()
            for dash in res.json().get("data", []):
                if dash.get("title") == title:
                    return dash.get("id", {}).get("id")
            return None
        except Exception as e:
            print(f"Lỗi tìm dashboard id: {e}")
            return None   