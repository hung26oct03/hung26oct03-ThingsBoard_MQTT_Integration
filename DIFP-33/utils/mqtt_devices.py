import paho.mqtt.client as mqtt
import random
import json
import time

class DeviceMQTT:
    def __init__(self, device_name, access_token, thingsboard_host, port=1883):
        self.device_name = device_name
        self.access_token = access_token
        self.host = thingsboard_host
        self.port = port
        self.connected = False
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(self.access_token)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print('Kết nối thành công')
        else:
            self.connected = False
            print('Kết nối thất bại')
            
    def on_publish(self, client, userdata, mid):
        print(f"[{self.device_name}] => đã gửi telemetry (msg_id: {mid})")
        time.sleep(1)
        
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print('Mất kết nối')
        
    def connect(self):
        try:
            # print(f'Check host: {self.host} - port: {self.port}')
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            time.sleep(1)
            return self.connected
        except Exception as e:
            print('Lỗi kết nối: ', e)
            return False
        
    def generate_telemetry_data(self):
        data = {
            'temperature': round(random.uniform(20.0, 35.0), 2),
            'heart_rate': round(random.uniform(60.0, 160.0), 2)
        }
        return data
    
    def publish_telemetry(self, data):
        if not self.connected:
            return False
        
        topic = 'v1/devices/me/telemetry'
        payload = json.dumps(data)
        
        result = self.client.publish(topic, payload, qos=1)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def publish_attributes(self, attributes):
        if not self.connected:
            return False
        
        topic = 'v1/devices/me/attributes'
        payload = json.dumps(attributes)
        
        result = self.client.publish(topic, payload, qos=1)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print('Đã ngắt kết nối OK')