# MQTT Connection Client

A simple and powerful MQTT client written in Python that provides the ability to connect to MQTT servers and receive messages.

## Features

- ✅ Easy connection to MQTT servers
- ✅ Authentication support (Username/Password)
- ✅ Subscribe to various topics
- ✅ Colorful message display in terminal
- ✅ Support for different QoS levels
- ✅ Complete message information display (time, topic, content)
- ✅ Error handling and reconnection
- ✅ Safe exit with Ctrl+C

## Installation and Setup

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Step 1: Clone the project

```bash
git clone <repository-url>
cd MQTT-Connection
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install paho-mqtt colorama python-dotenv
```

### Step 3: Run the program

#### Method 1: Interactive execution (recommended for beginners)

```bash
python mqtt_client.py
```

The program will ask you for the following information:
- MQTT server address
- Port (default: 1883)
- Username (optional)
- Password (optional)
- Client ID (optional)
- Topic to subscribe
- QoS level

#### Method 2: Using simple example

```bash
python simple_example.py
```

## Usage Guide

### Connecting to MQTT server

```python
from mqtt_client import MQTTClient

# Create client
client = MQTTClient()

# Connect to server
success = client.connect_to_broker(
    host="broker.hivemq.com",
    port=1883,
    username="your_username",  # optional
    password="your_password",  # optional
    client_id="my_client_id"   # optional
)

if success:
    print("Connection successful!")
else:
    print("Connection error!")
```

### Subscribe to topic

```python
# Subscribe to a topic
client.subscribe_to_topic("sensors/temperature", qos=0)

# Subscribe to multiple topics
topics = ["sensors/temperature", "sensors/humidity", "alerts/#"]
for topic in topics:
    client.subscribe_to_topic(topic)
```

### Send message

```python
# Send simple message
client.publish_message("sensors/temperature", "25.5")

# Send JSON message
import json
data = {"temperature": 25.5, "unit": "celsius", "sensor_id": "temp_01"}
message = json.dumps(data, ensure_ascii=False)
client.publish_message("sensors/temperature", message, qos=1)
```

### Connection management

```python
# Check connection status
status = client.get_status()
print(f"Connected: {status['connected']}")
print(f"Messages received: {status['message_count']}")
print(f"Subscribed topics: {status['subscribed_topics']}")

# Disconnect
client.disconnect()
```

## Free MQTT servers for testing

### 1. HiveMQ Public Broker
- **Host:** `broker.hivemq.com`
- **Port:** `1883` (unsecure) or `8883` (SSL)
- **Authentication:** Not required
- **Limitation:** Suitable for testing and development

### 2. Eclipse Mosquitto
- **Host:** `test.mosquitto.org`
- **Port:** `1883` (unsecure) or `8883` (SSL)
- **Authentication:** Not required
- **Limitation:** Suitable for testing

### 3. EMQX Public Broker
- **Host:** `broker.emqx.io`
- **Port:** `1883` (unsecure) or `8883` (SSL)
- **Authentication:** Not required
- **Limitation:** Suitable for testing

## Practical Examples

### Example 1: Sensor monitoring

```python
from mqtt_client import MQTTClient
import time

client = MQTTClient()

# Connect to server
if client.connect_to_broker("broker.hivemq.com"):
    # Subscribe to all sensors
    client.subscribe_to_topic("sensors/+/temperature")
    client.subscribe_to_topic("sensors/+/humidity")
    client.subscribe_to_topic("alerts/#")
    
    print("Monitoring sensors...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
```

### Example 2: Alert system

```python
from mqtt_client import MQTTClient
import json

class AlertSystem:
    def __init__(self):
        self.client = MQTTClient()
        # Override the on_message method
        self.client.on_message = self.handle_alert
    
    def handle_alert(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            if data.get('level') == 'critical':
                print(f"🚨 Critical Alert: {data.get('message')}")
                # Send notification or email
        except:
            pass
    
    def start_monitoring(self):
        if self.client.connect_to_broker("broker.hivemq.com"):
            self.client.subscribe_to_topic("alerts/critical")
            print("Alert system activated...")

# Usage
alert_system = AlertSystem()
alert_system.start_monitoring()
```

## Advanced Settings

### Using configuration file

Create a `.env` file:

```env
MQTT_HOST=broker.hivemq.com
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_CLIENT_ID=my_python_client
MQTT_TOPIC=sensors/temperature
```

And use it in code:

```python
from dotenv import load_dotenv
import os

load_dotenv()

client = MQTTClient()
client.connect_to_broker(
    host=os.getenv('MQTT_HOST'),
    port=int(os.getenv('MQTT_PORT', 1883)),
    username=os.getenv('MQTT_USERNAME'),
    password=os.getenv('MQTT_PASSWORD'),
    client_id=os.getenv('MQTT_CLIENT_ID')
)
```

### SSL/TLS Setup

```python
import ssl

# Setup SSL context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
client.client.tls_set_context(context)

# Connect with SSL
client.connect_to_broker("broker.hivemq.com", port=8883)
```

## Troubleshooting

### Common problems and solutions

#### 1. Connection error
```
✗ Connection error: [Errno 11001] getaddrinfo failed
```
**Solution:** Check that the server address is correct and internet connection is established.

#### 2. Authentication error
```
✗ Connection error: Connection refused - invalid username or password
```
**Solution:** Check username and password or use a server without authentication.

#### 3. Not receiving messages
**Possible solutions:**
- Check topic name correctness
- Ensure messages are being sent to the topic
- Check QoS level
- Use wildcards (`+` or `#`) for testing

#### 4. Unicode display issues
**Solution:** Make sure your terminal supports UTF-8.

### Enable diagnostic logs

```python
import logging

# Enable MQTT logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("paho")
logger.setLevel(logging.DEBUG)
```

## Contributing to the project

If you want to improve this project:

1. Fork it
2. Create a new branch
3. Commit your changes
4. Send a Pull Request

## License

This project is released under the MIT license.

## Support

If you have questions or encounter problems, you can:

- Create a new issue on GitHub
- Read MQTT documentation
- Get help from programming communities

---

**Note:** This client is designed for educational and development purposes. For production use, consider additional security settings.