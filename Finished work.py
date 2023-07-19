print("MQTT with Adafruit IO")
import time
import sys
import random
from Adafruit_IO import MQTTClient
import requests

# # Car Function
class Car:
    # Definite car sensor value
    def __init__(self):
        self.time_elapsed = 0                               # Set car running time
        self.engine_status = 0                              # Sensor for engine status (1-On/2-Off)
        self.speed_sensor = 0                               # Sensor for speed
        self.random_speed = random.randint(0,240)           # Random a speed value that it is belived to be relatively stable during the journey
        self.ex_temp_sensor = random.randint(-30,48)        # Temperature of the external evironment
        self.ECT_sensor = self.ex_temp_sensor + 5           # Sensor for ECT
        self.cab_temp_sensor = self.ex_temp_sensor + 10     # Sensor for cabin temperature
        self.fuel_sensor = random.randint(0,100)            # Sensor for fuel measuring
        self.exp_AC_temp = random.randint(20,25)            # Random an ideal temperature in cabin for the driver
        self.ECT_lock = False                               # Lock the first value of ECT when it comes to pass the standard value (75 oC)
        self.distance = 0                                   # Store distance from the main program                         
        self.car_problem = ["---"]                          # Store car_problem alert
        self.PC = [                                         # Car problem list and times when the car meets the problem during the trip
            ["Overheating", 1],
            ["Low fuel", 1],
            ["Out of fuel", 1], 
            ["Tire issue", 1],
            ["Low battery", 1], 
            ["Abnormal fuel loss", 1],  
            ["Filter Replacement", 1],
            ["Oil change", 1],
            ["Warming up", 1]
        ]

    # Power the engine
    def turn_on(self):
        self.engine_status = 1
        print(f'Power ON')
        print(f'AC is on')
    def turn_off(self):
        self.engine_status = 0
        print(f"Power OFF")
        print(f'AC is off')

    # Pass the distance value into Car class:
    def distance_receiver(self, origin_distance):
        self.distance = origin_distance

    # # Update Processing
    # 1. Diagnose Trouble Code
    def DTC(self):
        # Simulate a diagnosis check
        new_problems = []
        # Test the case
        test_to_append(new_problems, self.PC[0][0], self.ECT_sensor > 120)
        test_to_append(new_problems, self.PC[1][0], self.fuel_sensor < 20, self.fuel_sensor > 0)
        test_to_append(new_problems, self.PC[2][0], self.fuel_sensor == 0 )
        test_to_append(new_problems, self.PC[3][0], test_case(self.distance, 200, self.PC, 3))
        test_to_append(new_problems, self.PC[4][0], test_case(self.distance, 400, self.PC, 4))
        test_to_append(new_problems, self.PC[5][0], test_case(self.distance, 600, self.PC, 5))
        test_to_append(new_problems, self.PC[6][0], test_case(self.distance, 800, self.PC, 6))
        test_to_append(new_problems, self.PC[7][0], test_case(self.distance, 875, self.PC, 7))
        test_to_append(new_problems, self.PC[8][0], self.ECT_sensor < 75)

        # Add new problems to the list
        for new_problem in new_problems:
            for existing_problem in self.car_problem:
                if new_problem == existing_problem:
                    self.car_problem.remove(existing_problem)
        self.car_problem.extend(new_problems)
        
        # Delete the empty sign
        if len(self.car_problem) > 1 and ("---" in self.car_problem):
            self.car_problem.remove("---")
    # 2. Fuel_lossing_process
    def fuel_update(self):
        # Fuel consumption constants based on speed, AC, and temperature
        speed_consumption_rate = 0.015 
        AC_consumption_rate = 0.009    
        temp_consumption_rate = 0.006 
        speed_consumption = 0 

        if self.engine_status == 1:
            # Calculate fuel consumption based on speed
            speed_consumption += speed_consumption_rate * self.speed_sensor

            # Calculate additional fuel consumption if AC is ON
            speed_consumption += AC_consumption_rate 

            # Calculate additional fuel consumption based on temperature
            if self.ECT_sensor > 75:
                temp_consumption = temp_consumption_rate * (self.ECT_sensor - 75)
                speed_consumption += temp_consumption

        # Calculate remaining fuel after consumption
        self.fuel_sensor -= speed_consumption

        # Ensure remaining fuel is not negative
        if self.fuel_sensor < 0:
            self.fuel_sensor = 0
    # 3. AC_controller:
    def AC_update(self):
        if self.engine_status == 1:
            self.cab_temp_sensor = value_change(self.cab_temp_sensor, self.exp_AC_temp)
        else:
            self.cab_temp_sensor = value_change(self.cab_temp_sensor, self.ex_temp_sensor + 10)
    # 4. Speed_generator
    def speed_update(self): 
        acceleration = self.time_elapsed            # Acceleration value (2 km/h^2)
        deceleration = 2 * self.time_elapsed        # Deceleration value (1 km/h^2)
        
        if (self.engine_status == 1) & (self.fuel_sensor > 0) & (self.ECT_sensor >= 75):  
            if self.speed_sensor < self.random_speed:
                self.speed_sensor += acceleration
            else: 
                self.speed_sensor = random.randint(self.random_speed - 2, self.random_speed + 2)
        else:       
            if self.speed_sensor >= deceleration:
                self.speed_sensor -= deceleration
            else: self.speed_sensor = 0
    # 5. Temperature_of_car_engine(ECT)
    def ECT_update(self):
        cooling_rate = 0.1              # Cooling rate per unit of time
        temp_increase_above_75 = 0.2    # Base temperature increase per unit of speed
        warming_index = 3               # Engine self-warming index

        if self.engine_status == 1:
            if self.ECT_sensor >= 75:  
                if not self.ECT_lock:
                    self.ECT_lock = True
                    if self.ECT_sensor > 100:
                        self.ECT_sensor = random.randint(75,100)
                    self.ECT_initial = self.ECT_sensor
                    self.car_problem.remove("Warming up")
                    if len(self.car_problem) == 0:
                        self.car_problem.append("---") 
                self.ECT_sensor = self.ECT_initial + temp_increase_above_75 * self.speed_sensor - cooling_rate * self.time_elapsed 
            else: 
                self.ECT_sensor += warming_index * self.time_elapsed
        else:
            self.ECT_sensor = value_change(self.ECT_sensor, self.ex_temp_sensor)
    # 6. Totall Distance
    def distance_update(self):
        self.distance += self.speed_sensor * (self.time_elapsed/80)
    # 7. Update the engine status
    def update(self):
        self.fuel_update()
        self.AC_update()
        self.ECT_update()
        self.DTC()
        self.distance_update()
        self.speed_update()

    # # Return the car values
    # 1. Return the speed value
    def speed(self):
        return self.speed_sensor
    # 2. Return the temperature of engine
    def ECT(self):
        return self.ECT_sensor
    # 3. Return the temperature in the cabin
    def cabin_temp(self):
        return self.cab_temp_sensor
    # 4. Return the level of remain fuel 
    def fuel(self):
        return self.fuel_sensor
    # 5. Return the DCT
    def car_issue(self):
        return self.car_problem
    # 6. Return the distance update:
    def totall_distance(self):
        return self.distance

# # MQTT procedure (Adafruit-IO):
# 1. Subscribe
def subscribe(client , userdata , mid , granted_qos):
    print("Subscribe!!!")
# 2. Connecting
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

# 3. Disconnecting
def disconnected(client):
    print("Disconnected from the server!!!")
    sys.exit (1)
# 4. Message Annoucement 
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
        
# 5. Query the lastest data from a feed
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

# # Extra funtion:
# 1. Change the value
def value_change(first_value, last_value):
    if (first_value - last_value) < 0.5:
        first_value = last_value
    else:
        change_speed_value = (last_value - first_value)/4
        first_value += change_speed_value
    return first_value
# 2. Check if the case meets the conditons: 
def test_case(data, check_value, LP, num_case):
    ratio = data/(check_value*LP[num_case][1])
    if ratio > 1:
        LP[num_case][1] += int(ratio)
        return True
    else: 
        return False  
# 3. Check the condtions to print the problem
def test_to_append(result, case, *arg):
    all_condition = all(arg)
    if all_condition:
        result.append(case)
# 4. Check if there is a repetition between the sending data and existed data:
def check_rep(list,check_list):
    for key in list:
        if list[key] != check_list[key]:
            client.publish(key, list[key])


# Set the client registration for "client"
AIO_USERNAME = "---"                       # Add the valid information here
AIO_KEY = "---"                            # Add the valid information here
client = MQTTClient(AIO_USERNAME, AIO_KEY)

# Set procedure when one of those codes is executed 
client.on_connect = connected            
client.on_disconnect = disconnected     
client.on_message = message             # Supervise the upcomming message and send the message when it comes
client.on_subscribe = subscribe         # Subscribe to the feed

client.connect()  # Connect to the server 
# Keep connecting to the server and receiving the upcomming message from the server
client.loop_background()

# # Set up for car module:
# 1. Python Module
car = Car()
car.turn_on()
client.publish("Engine_Status", car.engine_status)
origin_distance = float(query_latest_data("Nhap API cua feed Distance", raw = False))
if origin_distance > 10000:
    origin_distance = 0
car.distance_receiver(origin_distance)
# 2. MQTT Module
client.publish("Car_problem", "---")
client.publish("AC_Adjust",car.exp_AC_temp)
url_feeds = "https://io.adafruit.com/api/v2/Steve12345/feeds" # Lay API cua mot feed bat ki roi xoa "/..." cuoi se ra vi du: API luc dau: https://io.adafruit.com/api/v2/Steve12345/feeds/ac-adjust

while True:
    # Power On
    if (car.engine_status == 1):
        # Time durations for the previous car run:
        car.time_elapsed = 10
        # Update car data
        car.update()
        # Forming data to public:
        feeds["AC_adjust"] = car.exp_AC_temp
        feeds["Engine_Status"] = car.engine_status
        feeds["Speed_sensor"] = car.speed()
        feeds["ECT_sensor"] = car.ECT()
        feeds["Fuel_sensor"] = car.fuel()
        feeds["Distance"] = car.totall_distance()
        feeds["Cabin_Temp_sensor"] = car.cabin_temp()
        Raw_car_issue = car.car_issue()
        feeds["Car_problem"] = ", ".join(Raw_car_issue)
        if "---" in Raw_car_issue:
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
        car.time_elapsed = 10
        # Update car data
        car.update()
        # Forming data to public:
        feeds["AC_adjust"] = car.exp_AC_temp
        feeds["Engine_Status"] = car.engine_status
        feeds["Speed_sensor"] = car.speed()
        feeds["ECT_sensor"] = car.ECT()
        feeds["Fuel_sensor"] = car.fuel()
        feeds["Distance"] = car.totall_distance()
        feeds["Cabin_Temp_sensor"] = car.cabin_temp()
        Raw_car_issue = car.car_issue()
        feeds["Car_problem"] = ", ".join(Raw_car_issue)
        if "---" in Raw_car_issue:
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
