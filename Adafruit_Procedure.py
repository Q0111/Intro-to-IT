print("MQTT with Adafruit IO")
import time
import sys
from Adafruit_IO import MQTTClient
import requests

# Query the lastest data from a feed
def query_latest_data(aio_url): 
    headers = {}
    # Remember to public your feed before running!!!
    x = (requests.get(url=aio_url, headers=headers, verify=True))
    raw_data = x.json()
    # print(f"Raw data is: \n {raw_data}")    # Delete the # if you know to know how does the raw_data form
    latest_data = raw_data["last_value"]
    print("Get latest value:", latest_data)
    return latest_data

# Set function for getting announcement when the MQTTClient code is executed

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe!!!")

def connected(client):
    print("Server connected ...")
    # Subscribe feed here:
    client.subscribe("AC_Adjust")
    client.subscribe("Cabin_Temp_sensor")
    client.subscribe("Car_problem")
    client.subscribe("Fuel_sensor")
    client.subscribe("Distance")
    client.subscribe("ECT_sensor")
    client.subscribe("Engine_Status")
    client.subscribe("Speed_sensor")

def disconnected(client):
    print("Disconnected from the server!!!")
    sys.exit (1)

def message(client , feed_id , payload): # Send the message when an upcoming message is taken place
    print(f" Recent message recieved from feed {feed_id}: {payload}")

# Set the client registration for "client"
AIO_USERNAME = "---" # Add the valid information here
AIO_KEY = "---"      # Add the valid information here
client = MQTTClient(AIO_USERNAME , AIO_KEY)

# Set procedure when one of those codes is executed 
client.on_connect = connected            
client.on_disconnect = disconnected     
client.on_message = message             # Supervise the upcomming message and send the message when it comes
client.on_subscribe = subscribe         # Subscribe to the feed

client.connect()                        # Connect to the server 
# Keep connecting to the server and receiving the upcomming message from the server
client.loop_background()        
while True:                             # Keep the program run with the server    
    
    # Receive the latest data from feed "AC_adjust"
    aio_url = "https://io.adafruit.com/api/v2/Steve12345/feeds/ac-adjust" # Add the valid information here
    latest_value = query_latest_data(aio_url)
    print (f"Latest value is: {latest_value}")
    
    time.sleep(10)
    pass
