import paho.mqtt.client as mqtt
import json
import time

class DeviceMQTT:
    def __init__(self, device_name, access_token, thingsboard_host, metric_type=None, port=1883):
        self.device_name = device_name
        self.access_token = access_token
        self.host = thingsboard_host
        self.port = port
        self.metric_type = metric_type
        self.connected = False
        self.published_messages = {}
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(self.access_token)
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f'[{self.device_name}] Kết nối thành công')
        else:
            self.connected = False
            print(f'[{self.device_name}] Kết nối thất bại')
            
    def on_publish(self, client, userdata, mid):
        msg_type = self.published_messages.pop(mid, "unknown")
        print(f"[{self.device_name}] => đã gửi {msg_type} (msg_id: {mid})")
        
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f'[{self.device_name}] Mất kết nối')
        
    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            time.sleep(1)
            return self.connected
        except Exception as e:
            print(f'[{self.device_name}] Lỗi kết nối: ', e)
            return False
    
    def publish_telemetry(self, data):
        if not self.connected:
            return False
        
        topic = 'v1/devices/me/telemetry'
        payload = json.dumps(data)
        
        result = self.client.publish(topic, payload, qos=1)
        self.published_messages[result.mid] = "telemetry"
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def publish_attributes(self, attributes):
        if not self.connected:
            return False
        
        topic = 'v1/devices/me/attributes'
        payload = json.dumps(attributes)
        print(f'Check payload: {payload}')
        result = self.client.publish(topic, payload, qos=1)
        self.published_messages[result.mid] = "attributes"
        result.wait_for_publish() 
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print(f'[{self.device_name}] Đã ngắt kết nối OK')