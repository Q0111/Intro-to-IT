print("MQTT with Adafruit IO")
import time
import random
import sys
from Adafruit_IO import MQTTClient
import requests

AIO_USERNAME = "---"
AIO_KEY = "---"

global_equation = ''

def init_global_equation():
    global global_equation
    headers = {}
    # Remember to public your feed before running!!!
    aio_url = "https://io.adafruit.com/api/v2/Steve12345/feeds/ac-adjust"
    x = (requests.get(url=aio_url, headers=headers, verify=True))
    data = x.json()
    print(f"Raw data is: \n {data}")
    global_equation = data["last_value"]
    print("Get latest value:", global_equation)

def modify_value(x1, x2, x3):
    result = eval(global_equation)
    print(result)
    return result


def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe!!!")

def connected(client):
    print("Server connected ...")
    client.subscribe("Distance")
    client.subscribe("Car_problem")
    client.subscribe("Cabin_Temp_sensor")

def disconnected(client):
    print("Disconnected from the server!!!")
    sys.exit (1)

def message(client , feed_id , payload):
    print(f"Received from feed {feed_id}: {payload}")
    if(feed_id == "equation"):
        global_equation = payload
        print(global_equation)

client = MQTTClient(AIO_USERNAME , AIO_KEY)

client.on_connect = connected  
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe

client.connect()
client.loop_background()
init_global_equation()

while True: 
    s1 = random.randint(20,70)
    s2 = random.randint(0,100)
    s3 = random.randint(0,14)
    client.publish("Distance", s1)
    client.publish("Car_problem", s2)
    client.publish("Cabin_Temp_sensor", s3)
    s4 = modify_value(s1, s2, s3)
    print(global_equation)
    print(s4)
    time.sleep(5)
    pass
    
