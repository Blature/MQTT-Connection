#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced MQTT Client example using configuration file
"""

from mqtt_client import MQTTClient
from dotenv import load_dotenv
import os
import json
import time
import ssl
from datetime import datetime

load_dotenv()

class AdvancedMQTTClient(MQTTClient):
    """Advanced MQTT Client class with additional features"""
    
    def __init__(self, config_file=None):
        super().__init__()
        self.config = self.load_config(config_file)
        self.message_log = []
        self.max_log_size = 1000
    
    def load_config(self, config_file=None):
        """Load configuration from .env file or environment variables"""
        if config_file:
            load_dotenv(config_file)
        
        config = {
            'host': os.getenv('MQTT_HOST', 'broker.hivemq.com'),
            'port': int(os.getenv('MQTT_PORT', 1883)),
            'username': os.getenv('MQTT_USERNAME'),
            'password': os.getenv('MQTT_PASSWORD'),
            'client_id': os.getenv('MQTT_CLIENT_ID', f'advanced_client_{int(time.time())}-sub'),
            'topic': os.getenv('MQTT_TOPIC', 'test/topic'),
            'qos': int(os.getenv('MQTT_QOS', 0)),
            'use_ssl': os.getenv('MQTT_USE_SSL', 'false').lower() == 'true',
            'ca_cert_path': os.getenv('MQTT_CA_CERT_PATH'),
            'cert_file_path': os.getenv('MQTT_CERT_FILE_PATH'),
            'key_file_path': os.getenv('MQTT_KEY_FILE_PATH')
        }
        
        return config
    
    def setup_ssl(self):
        """Setup SSL/TLS"""
        if not self.config['use_ssl']:
            return
        
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        # If custom certificate files exist
        if self.config['ca_cert_path']:
            context.load_verify_locations(self.config['ca_cert_path'])
        
        if self.config['cert_file_path'] and self.config['key_file_path']:
            context.load_cert_chain(self.config['cert_file_path'], self.config['key_file_path'])
        
        self.client.tls_set_context(context)
        print(f"SSL/TLS enabled")
    
    def on_message(self, client, userdata, msg):
        """Overridden to save messages in log"""
        # Call original method for display
        super().on_message(client, userdata, msg)
        
        # Save in log
        message_data = {
            'timestamp': datetime.now().isoformat(),
            'topic': msg.topic,
            'payload': msg.payload.decode('utf-8', errors='ignore'),
            'qos': msg.qos,
            'retain': msg.retain
        }
        
        self.message_log.append(message_data)
        
        # Limit log size
        if len(self.message_log) > self.max_log_size:
            self.message_log = self.message_log[-self.max_log_size:]
    
    def connect_with_config(self):
        """Connect using loaded configuration"""
        print(f"Connecting to {self.config['host']}:{self.config['port']}")
        print(f"Client ID: {self.config['client_id']}")
        
        # Setup SSL if needed
        if self.config['use_ssl']:
            self.setup_ssl()
        
        # Connect
        success = self.connect_to_broker(
            host=self.config['host'],
            port=self.config['port'],
            username=self.config['username'],
            password=self.config['password'],
            client_id=self.config['client_id']
        )
        
        return success
    
    def subscribe_to_default_topic(self):
        """Subscribe to default topic"""
        if self.config['topic']:
            return self.subscribe_to_topic(self.config['topic'], self.config['qos'])
        return False
    
    def save_message_log(self, filename=None):
        """Save message log to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mqtt_messages_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.message_log, f, ensure_ascii=False, indent=2)
            print(f"Message log saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving log: {e}")
            return False
    
    def get_message_statistics(self):
        """Statistics of received messages"""
        if not self.message_log:
            return {"total_messages": 0}
        
        topics = {}
        for msg in self.message_log:
            topic = msg['topic']
            topics[topic] = topics.get(topic, 0) + 1
        
        stats = {
            "total_messages": len(self.message_log),
            "unique_topics": len(topics),
            "topics_count": topics,
            "first_message_time": self.message_log[0]['timestamp'] if self.message_log else None,
            "last_message_time": self.message_log[-1]['timestamp'] if self.message_log else None
        }
        
        return stats
    
    def filter_messages_by_topic(self, topic_pattern):
        """Filter messages by topic"""
        filtered = []
        for msg in self.message_log:
            if topic_pattern in msg['topic'] or topic_pattern == '*':
                filtered.append(msg)
        return filtered
    
    def publish_json_message(self, topic, data, qos=0, retain=False):
        """Send JSON message"""
        try:
            json_message = json.dumps(data, ensure_ascii=False)
            return self.publish_message(topic, json_message, qos, retain)
        except Exception as e:
            print(f"Error sending JSON message: {e}")
            return False

def interactive_mode():
    """Advanced interactive mode"""
    print("=== Advanced MQTT Client ===")
    print("1. Auto connect with .env file")
    print("2. Manual connection")
    print("3. Exit")
    
    choice = input("Choose (1-3): ").strip()
    
    if choice == '3':
        return
    
    client = AdvancedMQTTClient()
    
    try:
        if choice == '1':
            # Auto connect
            if client.connect_with_config():
                if client.subscribe_to_default_topic():
                    print("\nMonitoring mode activated")
                    print("Available commands:")
                    print("- 'stats': Show statistics")
                    print("- 'save': Save log")
                    print("- 'filter <topic>': Filter messages")
                    print("- 'publish <topic> <message>': Send message")
                    print("- 'quit': Exit")
                    
                    while True:
                        try:
                            command = input("\n> ").strip().lower()
                            
                            if command == 'quit':
                                break
                            elif command == 'stats':
                                stats = client.get_message_statistics()
                                print(json.dumps(stats, ensure_ascii=False, indent=2))
                            elif command == 'save':
                                client.save_message_log()
                            elif command.startswith('filter '):
                                topic = command.split(' ', 1)[1]
                                filtered = client.filter_messages_by_topic(topic)
                                print(f"Messages related to '{topic}': {len(filtered)}")
                                for msg in filtered[-5:]:  # Last 5 messages
                                    print(f"  {msg['timestamp']}: {msg['topic']} -> {msg['payload'][:50]}...")
                            elif command.startswith('publish '):
                                parts = command.split(' ', 2)
                                if len(parts) >= 3:
                                    topic, message = parts[1], parts[2]
                                    client.publish_message(topic, message)
                                else:
                                    print("Format: publish <topic> <message>")
                            else:
                                print("Invalid command")
                                
                        except KeyboardInterrupt:
                            break
                        except Exception as e:
                            print(f"Error: {e}")
        
        elif choice == '2':
            # Manual connection
            print("\nEnter connection information:")
            host = input("Host: ").strip() or "broker.hivemq.com"
            port = int(input("Port (1883): ").strip() or "1883")
            username = input("Username (optional): ").strip() or None
            password = input("Password (optional): ").strip() or None
            client_id_input = input("Client ID (optional): ").strip()
            client_id = client_id_input + "-sub" if client_id_input else None
            
            if client.connect_to_broker(host, port, username, password, client_id):
                topic = input("Topic to subscribe: ").strip()
                if topic:
                    qos = int(input("QoS (0): ").strip() or "0")
                    client.subscribe_to_topic(topic, qos)
                
                print("\nPress Ctrl+C to exit")
                while True:
                    time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        
        # Auto save log
        if client.message_log:
            print("\nDo you want to save the message log? (y/n)")
            if input().lower().startswith('y'):
                client.save_message_log()

def monitoring_mode():
    """Simple monitoring mode"""
    client = AdvancedMQTTClient()
    
    try:
        if client.connect_with_config():
            # Subscribe to multiple topics
            topics = [
                "sensors/+/temperature",
                "sensors/+/humidity",
                "alerts/#",
                "status/#"
            ]
            
            for topic in topics:
                client.subscribe_to_topic(topic)
            
            print("\nMonitoring mode active - receiving messages...")
            print("Press Ctrl+C to exit\n")
            
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nExiting monitoring mode...")
        stats = client.get_message_statistics()
        print(f"Total messages received: {stats['total_messages']}")
        
        if stats['total_messages'] > 0:
            client.save_message_log()
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitoring_mode()
    else:
        interactive_mode()