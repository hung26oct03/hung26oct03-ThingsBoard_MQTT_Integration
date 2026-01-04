import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

class MQTTSubscriber:
    def __init__(self, client_id, broker_host="localhost", broker_port=1883):
        self.client_id = client_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id=client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        
        self.connected = False
        self.subscriptions = []
        self.messages = []
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f'[{self.client_id}] kết nối thành công')
        else:
            self.connected = False
            print(f'[{self.client_id}] kết nối thất bại')
        
    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"[{self.client_id}] đã subscribe OK => QoS: {granted_qos}")
    
    def on_message(self, client, userdata, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = msg.payload.decode('utf-8')
        
        msg_data = {
            'timestamp': timestamp,
            'topic': msg.topic,
            'message': message,
            'qos': msg.qos,
            'retain': msg.retain
        }
        self.messages.append(msg_data)
        print(f"[{self.client_id}] đã nhận được:")
        try:
            payload = json.loads(message)
            print(f"{timestamp}")
            print(f"heart rate: {payload.get('heart_rate')} bpm")
            print(f"spo2: {payload.get('spo2')}%")
            print(f"mesage id: {payload.get('message_id')}")
        except:
            print(f"Check: {message}")
        print()
        
    def connect(self):
        try:
            print(f"[{self.client_id}] đang kết nối đến {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            time.sleep(2)
        except Exception as e:
            print(f"Check: [{self.client_id}] lỗi kết nối: {e}")
            
    def subscribe(self, topic, qos):
        if not self.connected:
            print(f"[{self.client_id}] chưa kết nối đến broker")
            return False
        self.subscriptions.append((topic, qos))
        result = self.client.subscribe(topic, qos)
        return result[0] == mqtt.MQTT_ERR_SUCCESS
    
    def unsubscribe(self, topic):
        self.subscriptions = [(t, q) for t, q in self.subscriptions if t != topic]
        self.client.unsubscribe(topic)
        
    def show_message(self):
        if not self.messages:
            print('Check: Chưa có message')
        else:
            for idx, msg in enumerate(self.messages, 1):
                print(f"Check: {msg['message']}")
    
    def clear_messages(self):
        self.messages = []
        print(f"[{self.client_id}] đã xóa")
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        print(f"Check: [{self.client_id}] đã ngắt kết nối")