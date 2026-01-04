from mqtt_publisher import MQTTPublisher
from mqtt_subscriber import MQTTSubscriber
import time
import random
from datetime import datetime
import json

def run_main():
    BROKER_HOST = 'localhost'
    BROKER_PORT = 1883

    demo_publisher = MQTTPublisher('demo_publisher_01', BROKER_HOST, BROKER_PORT)
    demo_subscriber = MQTTSubscriber('demo_subscriber_01', BROKER_HOST, BROKER_PORT)
    
    demo_publisher.connect()
    demo_subscriber.connect()
    
    time.sleep(2)
    
    if not demo_publisher.connected or not demo_subscriber.connected:
        print("Check: Fail")
        return
    
    topic = 'healthcare/gateway-001/telemetry'
    demo_subscriber.subscribe(topic, qos=0)
    time.sleep(1)
    
    try:
        count = 0
        while True:
            count += 1
            
            payload = {
                "device_id": "gateway-001",
                "heart_rate": random.randint(60, 100),
                "spo2": random.randint(95, 100),
                "timestamp": datetime.now().isoformat()
            }
            
            success = demo_publisher.publish(topic, json.dumps(payload), qos=0)
            if not success:
                print(f"Fail")
            
            time.sleep(3)
                
    except KeyboardInterrupt:
        pass
    
    # demo_subscriber.show_message()
    
    demo_publisher.disconnect()
    demo_subscriber.disconnect()

if __name__ == '__main__':
    run_main()