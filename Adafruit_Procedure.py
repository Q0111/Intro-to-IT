print("MQTT with Adafruit IO")
import time
import sys
from Adafruit_IO import MQTTClient
import requests

def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe!!!")
def connected(client):
    print("Server connected ...")
    # Subscribe feed here (This is just the example, please adjusting to be suitable to your account):
    global feeds 
    feeds = {"AC_Adjust": 0,                # Thay the cac string trong day thanh ten cac feed cua ban, giu nguyen so 0 
            "Cabin_Temp_sensor": 0,         # Kiem tra o cau lenh duoi neu co lien quan den dictionary nay thi thay doi ten key.
            "Car_problem": 0, 
            "Fuel_sensor": 0, 
            "Distance": 0, 
            "ECT_sensor": 0, 
            "Engine_Status": 0, 
            "Speed_sensor": 0, 
            "Problem_indicator": 0} 
    for key in feeds:
            client.subscribe(key)
def disconnected(client):
    print("Disconnected from the server!!!")
    sys.exit (1)
def message(client , feed_id , payload,): # Send the message when an upcoming message is taken place
    print(f"Recent message recieved from feed {feed_id}: {payload}")
    if feed_id == "AC_Adjust":
        if  int(payload) != car.exp_AC_temp:
            car.exp_AC_temp = int(payload)


    if feed_id == "Engine_Status":
        if payload == '0':
            car.turn_off()     
        else:
            car.turn_on()   
    
    if feed_id == "Car_problem":
        if payload == "---":
            if "Warming up" in car.car_problem:
                car.car_problem.clear()
                car.car_problem.append("Warming up")
            else:
                car.car_problem.clear()
                car.car_problem.append("---")

# # Extra funtion:    
# 1. Query the lastest data from a feed
def query_latest_data(aio_url, raw): 
    headers = {}
    # Remember to public your feed before running!!!
    x = (requests.get(url=aio_url, headers=headers, verify=True))
    raw_data = x.json()
    if raw == True:
        return raw_data
    else:
        latest_data = raw_data["last_value"]
        return latest_data
# 2. Check if there is a repetition between the sending data and existed data:
def check_rep(list,check_list):
    for key in list:
        if list[key] != check_list[key]:
            client.publish(key, list[key])


# Set the client registration for "client"
AIO_USERNAME = "---"                       # Add the valid information here
AIO_KEY = "---"      # Add the valid information here
client = MQTTClient(AIO_USERNAME, AIO_KEY)

# Set procedure when one of those codes is executed 
client.on_connect = connected            
client.on_disconnect = disconnected     
client.on_message = message             # Supervise the upcomming message and send the message when it comes
client.on_subscribe = subscribe         # Subscribe to the feed

client.connect()  # Connect to the server 
# Keep connecting to the server and receiving the upcomming message from the server
client.loop_background() 
while True:                             # Keep the program run with the server    
    
    # Receive the latest data from feed "AC_adjust"
    aio_url = "https://io.adafruit.com/api/v2/Steve12345/feeds/ac-adjust" # Add the valid information here
    latest_value = query_latest_data(aio_url)
    print (f"Latest value is: {latest_value}")
    
    time.sleep(10)
    pass
