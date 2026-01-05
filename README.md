# IoT Car Simulation with Adafruit IO

This project simulates a **Smart Car Digital Twin** using Python. It models the physical behavior of a vehicle (engine status, fuel consumption, thermodynamics, speed) and connects it to an **Adafruit IO Dashboard** using the **MQTT protocol**.

The simulation acts as an IoT edge device that:
1. **Publishes** real-time sensor data to the cloud.
2. **Subscribes** to remote commands (e.g., turning the engine on/off or adjusting the AC) from the dashboard.
3. **Synchronizes** state intelligently to save bandwidth.

## 📋 Features

* **Physics Simulation:** Realistic calculation of fuel consumption based on speed, AC usage, and engine temperature.
* **Thermal Dynamics:** Simulates Engine Coolant Temperature (ECT) and Cabin Temperature changes based on operating status.
* **Diagnostic Trouble Codes (DTC):** Automatically detects and reports issues like "Overheat", "Low Fuel", or "Warming Up".
* **Bi-Directional MQTT:** * *Uplink:* Sends sensor data to Adafruit IO.
  * *Downlink:* Receives commands (Engine Start/Stop, AC Temp) from Adafruit IO.
* **Bandwidth Optimization:** Only publishes data when the local state differs from the server state using a "delta" check.
* **State Persistence:** Retrieves the last known odometer reading (distance) upon startup so data isn't lost between runs.

## 🛠️ Prerequisites

* **Python 3.x**
* **Adafruit IO Account:** You need a free account at [io.adafruit.com](https://io.adafruit.com).

### Required Python Libraries
Install the necessary dependencies using pip:

```bash
pip install adafruit-io requests
```

⚙️ Configuration
1. Adafruit IO Setup
Create a new Dashboard on Adafruit IO and create the following Feeds (case-sensitive):
- AC_Adjust
- Cabin_Temp_sensor
- Car_problem
- Fuel_sensor
- Distance
- ECT_sensor (Engine Coolant Temp)
- Engine_Status
- Speed_sensor
- Problem_indicator

2. Script Credentials
Open the Python script and update the credentials section with your specific Adafruit IO details:

```Python

# In the main script:
AIO_USERNAME = "YOUR_ADAFRUIT_USERNAME"
AIO_KEY = "YOUR_ADAFRUIT_IO_KEY"
```

# Update the URL with your username
url_feeds = "[https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds](https://io.adafruit.com/api/v2/YOUR_USERNAME/feeds)"
🚀 Usage
Run the simulation script:

```Bash
python car_simulation.py
```

Dashboard Interaction
1. Monitor: Watch the gauges update every 15 seconds as the car drives.
2. Control: * Use a Toggle Switch on your dashboard linked to Engine_Status to turn the car ON (1) / OFF (0).
3. Use a Slider linked to AC_Adjust to set the desired cabin temperature.

🧠 Code Structure
1. The Car Class (The Digital Twin)
This class encapsulates the state and physics of the vehicle.
** fuel_update(): Calculates fuel burn rate based on load.
** ECT_update(): Simulates engine heating and cooling cycles.
** DTC(): Logic for detecting system failures (e.g., auto-shutdown on empty fuel).

3. MQTT Handlers
** connected(): Subscribes to all relevant feeds upon connection.
** message(): Handles incoming control signals. If you change the AC on the dashboard, this function updates the Python object instantly.

3. The Main Loop
The script runs an infinite loop that:
1. Advances the simulation time by 20 seconds.
2. Updates all physics models.
3. Compares local data with the server via HTTP (check_rep).
4. Publishes only changed data to MQTT to ensure efficiency.
5. Sleeps for 15 seconds to rate-limit the API calls.

⚠️ Notes
** Safety Logic: The car will automatically turn off (car.turn_off()) if fuel reaches 0%.
** Reset on Exit: When the script finishes (or breaks the loop), it resets sensor values to 0 to indicate the car is offline.
