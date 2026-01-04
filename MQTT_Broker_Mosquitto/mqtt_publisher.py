import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

class MQTTPublisher:
    def __init__(self, client_id, broker_host="localhost", broker_port=1883):
        self.client_id = client_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print('Kết nối thành công')
        else:
            self.connected = False
            print('Kết nối thất bại')
            
    def on_publish(self, client, userdata, mid):
        print(f"[{self.client_id}] message đã được gửi => mid: {mid}")
        
    def publish(self, topic, message, qos, retain=False):
        if not self.connected:
            print(f"Lỗi: [{self.client_id}] không kết nối đến broker được")
            return False

        result = self.client.publish(topic, message, qos=qos, retain=retain)
        return result.rc == mqtt.MQTT_ERR_SUCCESS
    
    
    def connect(self):
        try:
            print(f"[{self.client_id}] đang kết nối đến {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(1)
        except Exception as e:
            print(f"Check: [{self.client_id}] Lỗi kết nối: {e}")
        
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print(f"Check: [{self.client_id}] Đã ngắt kết nối")