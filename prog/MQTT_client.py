from paho.mqtt.client import Client
from datetime import datetime as datetime

client=Client(client_id="IDSL-00a")
client.connect('localhost')
topic_test1 = "test/1"
topic_test2 = "test/2"
client.subscribe(topic_test1)
for k in range(100):
    now=datetime.utcnow()
    print('publishing ',format(now)+' '+format(k))
    
    client.publish(topic=topic_test1,payload=format(now)+' '+format(k))
