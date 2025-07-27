#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT Connection Client
This file provides a simple MQTT client for connecting to servers and receiving messages
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from colorama import Fore, Back, Style, init
import sys
import signal

# Initialize colorama for colored output
init(autoreset=True)

class MQTTClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self.subscribed_topics = []
        self.message_count = 0
        
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
    
    def on_message(self, client, userdata, msg):
        """Callback for receiving messages"""
        self.message_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Try to decode message as JSON
            message_str = msg.payload.decode('utf-8')
            try:
                message_json = json.loads(message_str)
                message_display = json.dumps(message_json, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                message_display = message_str
        except UnicodeDecodeError:
            message_display = f"[Binary Data - {len(msg.payload)} bytes]"
        
        print(f"\n{Back.BLUE}{Fore.WHITE} New Message #{self.message_count} {Style.RESET_ALL}")
        print(f"{Fore.CYAN}Time: {timestamp}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Topic: {msg.topic}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}QoS: {msg.qos}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Retain: {msg.retain}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Message Content:{Style.RESET_ALL}")
        print(f"{Fore.LIGHTWHITE_EX}{message_display}{Style.RESET_ALL}")
        print("-" * 60)
    
    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for subscribe confirmation"""
        print(f"{Fore.GREEN}✓ Successfully subscribed to topic (QoS: {granted_qos[0]}){Style.RESET_ALL}")
    
    def on_unsubscribe(self, client, userdata, mid):
        """Callback for unsubscribe confirmation"""
        print(f"{Fore.BLUE}ℹ Unsubscribed from topic{Style.RESET_ALL}")
    
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
            self.client.on_message = self.on_message
            self.client.on_subscribe = self.on_subscribe
            self.client.on_unsubscribe = self.on_unsubscribe
            
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
    
    def subscribe_to_topic(self, topic, qos=0):
        """Subscribe to a topic"""
        if not self.connected:
            print(f"{Fore.RED}✗ Please connect to server first{Style.RESET_ALL}")
            return False
        
        try:
            result = self.client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.subscribed_topics.append(topic)
                print(f"{Fore.YELLOW}Subscribing to topic: {topic}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}✗ Subscribe error: {result[0]}{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Subscribe error: {str(e)}{Style.RESET_ALL}")
            return False
    
    def unsubscribe_from_topic(self, topic):
        """Unsubscribe from a topic"""
        if not self.connected:
            print(f"{Fore.RED}✗ Not connected to server{Style.RESET_ALL}")
            return False
        
        try:
            result = self.client.unsubscribe(topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                if topic in self.subscribed_topics:
                    self.subscribed_topics.remove(topic)
                print(f"{Fore.BLUE}ℹ Unsubscribed from topic {topic}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}✗ Unsubscribe error: {result[0]}{Style.RESET_ALL}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Unsubscribe error: {str(e)}{Style.RESET_ALL}")
            return False
    
    def publish_message(self, topic, message, qos=0, retain=False):
        """Send message to a topic"""
        if not self.connected:
            print(f"{Fore.RED}✗ Please connect to server first{Style.RESET_ALL}")
            return False
        
        try:
            result = self.client.publish(topic, message, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"{Fore.GREEN}✓ Message successfully sent to {topic}{Style.RESET_ALL}")
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
    
    def get_status(self):
        """Get connection status"""
        status = {
            'connected': self.connected,
            'subscribed_topics': self.subscribed_topics,
            'message_count': self.message_count
        }
        return status

def signal_handler(sig, frame):
    """Handler for Ctrl+C"""
    print(f"\n{Fore.YELLOW}\nReceived exit signal...{Style.RESET_ALL}")
    if 'mqtt_client' in globals():
        mqtt_client.disconnect()
    print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
    sys.exit(0)

def main():
    """Main program function"""
    global mqtt_client
    
    # Set signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Back.GREEN}{Fore.WHITE} MQTT Client {Style.RESET_ALL}")
    print(f"{Fore.CYAN}Press Ctrl+C to exit the program{Style.RESET_ALL}\n")
    
    mqtt_client = MQTTClient()
    
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
        client_id = client_id_input + "-sub" if client_id_input else None
        
  
        if mqtt_client.connect_to_broker(host, port, username, password, client_id):
            

            topic = input(f"\n{Fore.CYAN}Topic to subscribe (example: test/topic): {Style.RESET_ALL}").strip()
            if topic:
                qos_input = input(f"{Fore.CYAN}QoS (0, 1, 2 - default: 0): {Style.RESET_ALL}").strip()
                qos = int(qos_input) if qos_input in ['0', '1', '2'] else 0
                
                if mqtt_client.subscribe_to_topic(topic, qos):
                    print(f"\n{Fore.GREEN}✓ Ready to receive messages...{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}\n")
                    
       
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        pass
            else:
                print(f"{Fore.YELLOW}⚠ No topic entered, only connection established{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Press Ctrl+C to exit{Style.RESET_ALL}")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Fore.RED}✗ Unexpected error: {str(e)}{Style.RESET_ALL}")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()