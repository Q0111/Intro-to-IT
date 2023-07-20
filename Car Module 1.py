import time
import random

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
        self.distance = origin_distance
# # Proccessing data
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

    def CT_update(self): # Cabin temp update
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

    def ECT_update(self):
        cooling_rate = 0.1
        temp_increase = 0.2
        warming_index = 3 
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
    # Supporting function
    @staticmethod
    def _value_change(first_value, last_value):
        if abs(first_value - last_value) < 0.5:
            return last_value
        change_speed_value = (last_value - first_value) / 4
        return first_value + change_speed_value

# Set the car environment
car = Car()
distance = 0                                                        # Can be adjusted (received from Adafruit)
start_time = 0
end_time = 0

# Turn on the engine
car.turn_on()

# Run Processing
while True:

    # Time durations for the previous car run:
    car.time_elapsed = end_time - start_time

    # Set the start time:
    start_time = time.time()

    # Calculate distance:
    distance += car.speed_sensor * (car.time_elapsed/60)
    car.distance_receiver(distance)

    # Update car data
    car.update()
    
    # Print current data
    print(f"Speed: {car.speed()} km/h")
    print(f"ECT: {car.ECT()} °C")
    print(f"External temperature: {car.ex_temp_sensor}")
    print(f"Fuel: {car.fuel()}%")
    print(f"Total distance: {car.distance} km")
    print(f"Diagnosis: {car.car_issue()}")

    # Check if any problems were fixed or appear
    if ("---" not in car.car_problem): 
        response = input(f"Did you fix the problem'? Y/N: ")
        if response == "Y":
            car.car_problem.clear()
            car.car_problem.add("None")
    
    # Check if the user want to stop the car:
    ask = input("Do you want to stop the car Y/N: ")
    if ask == "Y":
        car.turn_off()
        break
    
    # Set the end time
    end_time = time.time() 

    print("------------------------------------------------------------")

# Stop Processing
while car.speed() > 0: 
    
    # Calculate distance:
    distance += car.speed_sensor * (3/60)
    car.distance_receiver(distance)
    
    # Update car data
    car.update()
    # Print current data
    print(f"Speed: {car.speed()} km/h")
    print(f"ECT: {car.ECT()} °C")
    print(f"External temperature: {car.ex_temp_sensor}")
    print(f"Fuel: {car.fuel()}%")
    print(f"Diagnosis: {car.car_issue()}")
    print("-----------------------------------------------------------")
    time.sleep(3)

