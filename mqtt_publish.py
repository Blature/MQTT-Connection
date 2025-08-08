#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT Publisher Client
This file provides a simple MQTT client for connecting to servers and publishing messages
"""

import paho.mqtt.client as mqtt
import json
import time
import os
from datetime import datetime
from colorama import Fore, Back, Style, init
import sys
import signal

# Initialize colorama for colored output
init(autoreset=True)

class MQTTPublisher:
    def __init__(self):
        self.client = None
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback for server connection"""
        if rc == 0:
            self.connected = True
            print(f"{Fore.GREEN}✓ Successfully connected to MQTT server!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Connection code: {rc}{Style.RESET_ALL}")
        else:
            self.connected = False
            error_messages = {
                1: "Connection refused - Invalid protocol version",
                2: "Connection refused - Invalid client identifier",
                3: "Connection refused - Server unavailable",
                4: "Connection refused - Bad username or password",
                5: "Connection refused - Not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error - Code: {rc}")
            print(f"{Fore.RED}✗ Connection error: {error_msg}{Style.RESET_ALL}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback for disconnection"""
        self.connected = False
        if rc != 0:
            print(f"{Fore.YELLOW}⚠ Connection unexpectedly lost{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}ℹ Connection successfully closed{Style.RESET_ALL}")
    
    def on_publish(self, client, userdata, mid):
        """Callback for publish confirmation"""
        print(f"{Fore.GREEN}✓ Message successfully published (Message ID: {mid}){Style.RESET_ALL}")
    
    def connect_to_broker(self, host, port=1883, username=None, password=None, client_id=None):
        """Connect to MQTT broker"""
        try:
            # Create MQTT client
            if client_id:
                self.client = mqtt.Client(client_id=client_id)
            else:
                self.client = mqtt.Client()
            
            # Set callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            # Set authentication if provided
            if username and password:
                self.client.username_pw_set(username, password)
                print(f"{Fore.CYAN}ℹ Authentication with username configured{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}Connecting to {host}:{port}...{Style.RESET_ALL}")
            
            # Connect to broker
            self.client.connect(host, port, 60)
            
            # Start loop for message processing
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                raise Exception("Connection timeout to server")
                
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Connection error: {str(e)}{Style.RESET_ALL}")
            return False
    
    def publish_message(self, topic, message, qos=0, retain=False):
        """Send message to a topic"""
        if not self.connected:
            print(f"{Fore.RED}✗ Please connect to server first{Style.RESET_ALL}")
            return False
        
        try:
            result = self.client.publish(topic, message, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"{Fore.GREEN}✓ Message queued for publishing to {topic}{Style.RESET_ALL}")
                # Wait a bit for the publish callback
                time.sleep(0.5)
                return True
            else:
                print(f"{Fore.RED}✗ Message send error: {result.rc}{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Message send error: {str(e)}{Style.RESET_ALL}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print(f"{Fore.BLUE}ℹ Disconnecting...{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠ No connection to disconnect{Style.RESET_ALL}")

def load_payload():
    """Load payload from payload.json file"""
    payload_file = "payload.json"
    
    if not os.path.exists(payload_file):
        print(f"{Fore.RED}✗ payload.json file not found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please create a payload.json file with your message content{Style.RESET_ALL}")
        return None
    
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        print(f"{Fore.GREEN}✓ Payload loaded from {payload_file}{Style.RESET_ALL}")
        return json.dumps(payload, ensure_ascii=False)
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}✗ Invalid JSON in payload.json: {str(e)}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}✗ Error reading payload.json: {str(e)}{Style.RESET_ALL}")
        return None

def signal_handler(sig, frame):
    """Handler for Ctrl+C"""
    print(f"\n{Fore.YELLOW}\nReceived exit signal...{Style.RESET_ALL}")
    if 'mqtt_publisher' in globals():
        mqtt_publisher.disconnect()
    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
    sys.exit(0)

def main():
    """Main program function"""
    global mqtt_publisher
    
    # Set signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Back.GREEN}{Fore.WHITE} MQTT Publisher {Style.RESET_ALL}")
    print(f"{Fore.CYAN}Press Ctrl+C to exit the program{Style.RESET_ALL}\n")
    
    mqtt_publisher = MQTTPublisher()
    
    # Load payload first
    payload = load_payload()
    if payload is None:
        print(f"{Fore.RED}Cannot proceed without valid payload{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Payload to be sent:{Style.RESET_ALL}")
    print(f"{Fore.LIGHTWHITE_EX}{payload}{Style.RESET_ALL}\n")
    
    # Get connection information from user
    try:
        print(f"{Fore.YELLOW}Please enter connection information:{Style.RESET_ALL}")
        host = input(f"{Fore.CYAN}Server address (example: broker.hivemq.com): {Style.RESET_ALL}").strip()
        if not host:
            host = "broker.hivemq.com"
            print(f"{Fore.BLUE}Using default server: {host}{Style.RESET_ALL}")
        
        port_input = input(f"{Fore.CYAN}Port (default: 1883): {Style.RESET_ALL}").strip()
        port = int(port_input) if port_input else 1883
        
        username = input(f"{Fore.CYAN}Username (optional): {Style.RESET_ALL}").strip() or None
        password = input(f"{Fore.CYAN}Password (optional): {Style.RESET_ALL}").strip() or None
        client_id_input = input(f"{Fore.CYAN}Client ID (optional): {Style.RESET_ALL}").strip()
        client_id = client_id_input + "-pub" if client_id_input else None
        
        if mqtt_publisher.connect_to_broker(host, port, username, password, client_id):
            # Get topic and QoS
            topic = input(f"\n{Fore.CYAN}Topic to publish to (example: test/topic): {Style.RESET_ALL}").strip()
            if not topic:
                print(f"{Fore.RED}✗ Topic is required for publishing{Style.RESET_ALL}")
                return
            
            qos_input = input(f"{Fore.CYAN}QoS (0, 1, 2 - default: 0): {Style.RESET_ALL}").strip()
            qos = int(qos_input) if qos_input in ['0', '1', '2'] else 0
            
            retain_input = input(f"{Fore.CYAN}Retain message? (y/n - default: n): {Style.RESET_ALL}").strip().lower()
            retain = retain_input == 'y' or retain_input == 'yes'
            
            # Publish the message
            print(f"\n{Fore.YELLOW}Publishing message...{Style.RESET_ALL}")
            if mqtt_publisher.publish_message(topic, payload, qos, retain):
                print(f"\n{Fore.GREEN}✓ Message published successfully!{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Topic: {topic}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}QoS: {qos}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Retain: {retain}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to publish message{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Fore.RED}✗ Unexpected error: {str(e)}{Style.RESET_ALL}")
    finally:
        mqtt_publisher.disconnect()
        time.sleep(1)  # Give time for disconnection

if __name__ == "__main__":
    main()