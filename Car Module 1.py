import time

class Car:
    def __init__(self):
        self.engine_on = False
        self.speed = 0
        self.temperature = 0
        self.fuel = 100
        self.distance = 0

    def turn_on_engine(self):
        self.engine_on = True

    def turn_off_engine(self):
        self.engine_on = False

    def measure_speed(self):
        return self.speed

    def measure_temperature(self):
        return self.temperature

    def measure_fuel(self):
        return self.fuel

    def measure_distance(self):
        return self.distance

    def diagnose_problems(self):
        # Simulate a diagnosis check
        if self.temperature > 100:
            return "Overheating"
        if self.fuel < 20:
            return "Low fuel"
        return "No problems"

    def control_air_conditioner(self, is_on):
        if is_on:
            print("Air conditioner turned on")
        else:
            print("Air conditioner turned off")

    def update(self):
        # Simulate car behavior and update data
        if self.engine_on:
            self.speed += 10
            self.temperature += 1
            self.fuel -= 1
            self.distance += self.speed / 3600  # Assuming speed is in km/h

car = Car()

# Turn on the engine
car.turn_on_engine()

# Simulate car behavior and print data for a duration of 10 seconds
start_time = time.time()
while time.time() - start_time < 10:
    # Update car data
    car.update()

    # Print current data
    print(f"Speed: {car.measure_speed()} km/h")
    print(f"Temperature: {car.measure_temperature()} °C")
    print(f"Fuel: {car.measure_fuel()}%")
    print(f"Distance: {car.measure_distance()} km")
    print(f"Diagnosis: {car.diagnose_problems()}")
    print()

    # Simulate delay between updates
    time.sleep(3)

# Turn off the engine
car.turn_off_engine()
