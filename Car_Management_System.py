print("MQTT with Adafruit IO")
import time
import sys
import random
from Adafruit_IO import MQTTClient
import requests

# Module Car for Simulation: 
class Car:
    def __init__(self):
        self.time_elapsed = 0
        self.engine_status = 0
        self.speed_sensor = 0
        self.exp_speed = random.randint(0, 240)
        self.ex_temp_sensor = random.randint(-30, 48)
        self.ECT_sensor = self.ex_temp_sensor + 5
        self.ECT_lock = 0
        self.cab_temp_sensor = self.ex_temp_sensor + 10
        self.fuel_sensor = random.randint(0, 100)
        self.exp_AC = random.randint(20, 25)
        self.distance = 0
        self.car_problem = set()
        self.PC = ["Overheat",
                   "Low fuel", 
                   "Out of fuel", 
                   "Warming up"]

    def turn_on(self):
        self.engine_status = 1
        print('Power ON')
        print('AC is on')

    def turn_off(self):
        self.engine_status = 0
        print("Power OFF")
        print('AC is off')

    def distance_receiver(self, origin_distance):
        self.distance = 0 if origin_distance > 1000 else origin_distance 
    
    # ---- Simulate the operating of Car ------
    # DTC - Alert the driver for current car problem: Low fuel, Overheated Engine, ...
    def DTC(self):
        new_problem =[] 
        if self.ECT_sensor > 120:
            new_problem.append(self.PC[0])
        if self.fuel_sensor < 20:
            if self.fuel_sensor == 0:
                new_problem.append(self.PC[1])
                self.turn_off()
            else: 
                new_problem.append(self.PC[2])
        if self.ECT_sensor < 75:
            new_problem.append(self.PC[3])
        else:
            self.car_problem.discard("Warming up")
        
        # Update and check list of car problems:
        self.car_problem.update(problem for problem in new_problem)
        if len(self.car_problem) == 0: 
            self.car_problem.add("None")
        else: 
            self.car_problem.discard("None")


    def fuel_update(self):
        speed_consumption_rate = 0.0015 * self.time_elapsed
        AC_consumption_rate = 0.0009 * self.time_elapsed
        temp_consumption_rate = 0.0006 * self.time_elapsed
        speed_consumption = speed_consumption_rate * self.speed_sensor + AC_consumption_rate if self.engine_status == 1 else 0
        speed_consumption += temp_consumption_rate * max(0, self.ECT_sensor - 75) 
        self.fuel_sensor = self.fuel_sensor - speed_consumption if (self.fuel_sensor > speed_consumption_rate) else 0

    # Update the cabin temperature:
    def CT_update(self): 
        if self.engine_status == 1:
            self.cab_temp_sensor = self._value_change(self.cab_temp_sensor, self.exp_AC)
        else:
            self.cab_temp_sensor = self._value_change(self.cab_temp_sensor, self.ex_temp_sensor + 10)

    def speed_update(self): 
        acceleration = self.time_elapsed
        deceleration = 2 * self.time_elapsed
        if self.engine_status == 1 and self.ECT_sensor >= 75:  
            self.speed_sensor = min(self.exp_speed, self.speed_sensor + acceleration) if self.speed_sensor != self.exp_speed else random.randint(self.exp_speed -2, self.exp_speed -2)
        else:       
            self.speed_sensor = max(0, self.speed_sensor - deceleration)

    # Update the car's engine temperature:
    def ECT_update(self):
        cooling_rate = 0.1
        temp_increase = 0.2
        warming_index = 6
        if self.engine_status == 1:
            if self.ECT_sensor < 75:
                self.ECT_sensor += warming_index
                self.ECT_lock = self.ECT_sensor
            else:
                self.ECT_lock = random.randint(75, 90) if self.ECT_sensor > 90 else self.ECT_sensor
                self.ECT_sensor = self.ECT_lock + temp_increase * self.speed_sensor - cooling_rate * self.time_elapsed 
        else:
            self.ECT_sensor = self._value_change(self.ECT_sensor, self.ex_temp_sensor)

    def distance_update(self):
        self.distance += self.speed_sensor * (self.time_elapsed / 80)

    # Function for trigger car's sensor and status update:
    def update(self):
        self.ECT_update()
        self.speed_update()
        self.fuel_update()
        self.CT_update()
        self.distance_update()
        self.DTC()
    
    # Print the car value: 
    def speed(self):
        return self.speed_sensor
    def ECT(self):
        return self.ECT_sensor
    def cabin_temp(self):
        return self.cab_temp_sensor
    def fuel(self):
        return self.fuel_sensor
    def car_issue(self):
        return list(self.car_problem)
    def totall_distance(self):
        return self.distance
    
    # Supportive function
    @staticmethod
    def _value_change(first_value, last_value):
        if abs(first_value - last_value) < 0.5:
            return last_value
        change_speed_value = (last_value - first_value) / 4
        return first_value + change_speed_value

# --- Methods support for Adafruit connection ----
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe!!!")
    
def connected(client):
    print("Server connected ...")
    global feeds 
    feeds = {"AC_Adjust": 0,                
            "Cabin_Temp_sensor": 0,         
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

# Processing Payload Receiving
def message(client , feed_id , payload,): 
    print(f"Recent message recieved from feed {feed_id}: {payload}")
    
    if feed_id == "AC_Adjust":
        if  int(payload) != car.exp_AC:
            car.exp_AC = int(payload)
    elif feed_id == "Engine_Status":
        if payload == '0':
            car.turn_off()     
        else:
            car.turn_on()   
    elif feed_id == "Car_problem":
        if payload == "---":
            if "Warming up" in car.car_problem:
                car.car_problem.clear()
                car.car_problem.add("Warming up")
            else:
                car.car_problem.clear()
                car.car_problem.add("None")
    else: None

# --- Support Function ---

# Query the lastest data from a feed:
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

def check_rep(list,check_list):
    for key in list:
        if list[key] != check_list[key]:
            client.publish(key, list[key])

# --- Connection Configuration and Intial Setup ---

# Set the client registration for "client"
AIO_USERNAME = "---"                       # Input user's id
AIO_KEY = "---"                            # Input AIO_key
client = MQTTClient(AIO_USERNAME, AIO_KEY)

# Setup the Adafruit connection configuration: 
client.on_connect = connected            
client.on_disconnect = disconnected     
client.on_message = message             
client.on_subscribe = subscribe         

client.connect() 
client.loop_background()

# Set an instance of Car Module
car = Car()
car.turn_on()

# Retrieve the latest total distance record from the Dashboard
origin_distance = float(query_latest_data("https://io.adafruit.com/api/v2/Steve12345/feeds/distance", raw = False))
car.distance_receiver(origin_distance)

# MQTT Module
url_feeds = "https://io.adafruit.com/api/v2/Steve12345/feeds"     # Link to feeds' board of the user account 

while True:
    # Power On
    if (car.engine_status == 1):
        # Time durations for the previous car run:
        car.time_elapsed = 20
        # Update car data
        car.update()
        # Forming data to public:
        feeds["AC_Adjust"] = car.exp_AC
        #print(f"AC temperature: {car.exp_AC}")
        feeds["Engine_Status"] = car.engine_status
        feeds["Speed_sensor"] = car.speed()
        feeds["ECT_sensor"] = car.ECT()
        feeds["Fuel_sensor"] = car.fuel()
        feeds["Distance"] = car.totall_distance()
        feeds["Cabin_Temp_sensor"] = car.cabin_temp()
        Raw_car_issue = car.car_issue()
        feeds["Car_problem"] = ", ".join(Raw_car_issue)
        if "None" in Raw_car_issue:
            feeds["Problem_indicator"] = 0
        else:
            feeds["Problem_indicator"] = 1
        check = feeds.copy()
        a = query_latest_data(url_feeds, raw = True)
        for info_feed in a:
            for key in check:
                if info_feed.get("name") == key:
                    value = info_feed.get("last_value")
                    if isinstance(value, str) and value.isdigit():
                            value = int(value) 
                    elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                            value = float(value) 
                    check[key] = value   
        # Print current data
        check_rep(feeds, check)
        print("------------------------------------------------------------")

    # Power Off
    elif (car.speed() > 0):
        # Time durations for the previous car run:
        car.time_elapsed = 20
        # Update car data
        car.update()
        # Forming data to public:
        feeds["AC_Adjust"] = car.exp_AC
        feeds["Engine_Status"] = car.engine_status
        feeds["Speed_sensor"] = car.speed()
        feeds["ECT_sensor"] = car.ECT()
        feeds["Fuel_sensor"] = car.fuel()
        feeds["Distance"] = car.totall_distance()
        feeds["Cabin_Temp_sensor"] = car.cabin_temp()
        Raw_car_issue = car.car_issue()
        feeds["Car_problem"] = ", ".join(Raw_car_issue)
        if "None" in Raw_car_issue:
            feeds["Problem_indicator"] = 0
        else:
            feeds["Problem_indicator"] = 1
        check = feeds.copy()
        a = query_latest_data(url_feeds, raw = True)
        for info_feed in a:
            for key in check:
                if info_feed.get("name") == key:
                    value = info_feed.get("last_value")
                    if isinstance(value, str) and value.isdigit():
                            value = int(value) 
                    elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                            value = float(value) 
                    check[key] = value   
        # Print current data
        check_rep(feeds, check)
           
        print("------------------------------------------------------------") 
    else:
        break
    time.sleep(15)

# Reset the default value and Disconnect to Dashboard:
client.publish("AC_Adjust",0)
client.publish("Cabin_Temp_sensor",0)
client.publish("Car_problem","None")
client.publish("Fuel_sensor",0)
client.publish("Distance",0)
client.publish("ECT_sensor",0)
client.publish("Speed_sensor",0)
client.publish("AC_Adjust",0)
client.publish("Problem_indicator",0)
client.disconnect()
