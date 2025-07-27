#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple example for quick MQTT connection
"""

from mqtt_client import MQTTClient
import time

def quick_connect_example():
    """Quick connection example"""
    
    # Create client
    client = MQTTClient()
    
    # Connection information (you can change these)
    HOST = "broker.hivemq.com"  # Free HiveMQ server
    PORT = 1883
    USERNAME = None  # Enter if needed
    PASSWORD = None  # Enter if needed
    CLIENT_ID = "my_python_client_123-sub"
    TOPIC = "test/python/mqtt"  # Desired topic
    
    try:
        print("Starting connection...")
        
        # Connect to server
        if client.connect_to_broker(HOST, PORT, USERNAME, PASSWORD, CLIENT_ID):
            print(f"Connection successful! Subscribing to {TOPIC}")
            
            # Subscribe to topic
            if client.subscribe_to_topic(TOPIC, qos=0):
                print("Ready to receive messages...")
                print("For testing, you can send messages from another MQTT client")
                print("Press Ctrl+C to exit\n")
                
                # Send a test message
                test_message = "Hello! This is a test message from Python"
                client.publish_message(TOPIC, test_message)
                
                # Keep program running to receive messages
                while True:
                    time.sleep(1)
                    
        else:
            print("Connection error!")
            
    except KeyboardInterrupt:
        print("\nExiting program...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("Connection closed.")

if __name__ == "__main__":
    quick_connect_example()