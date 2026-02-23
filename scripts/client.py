import time
import websocket
import threading
import os
import json
import datetime
import queue
import asyncio
from websocket import create_connection
import requests
from urllib.error import HTTPError
import urllib.request
import http.client
import asyncio
import threading
import _thread
import rel
import subprocess
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from enc import SecureMessage
try:
    import thread
except ImportError:
    import _thread as thread
import time
import cProfile



SERVER_URL = "ws://192.168.2.225/ws/?id=agonxheladini001@gmail.com&type=device&hardware=48"  # Change to your server
RECONNECT_DELAY = 0.1  # Seconds between retries

msg = { "header":{ "from": "agonxheladini001@gmail.com", "from_type": "device", "to": "agonxheladini001@gmail.com", "to_type": "vue", "msg_type": "pong", "hardware_id": "48", "sensor_id":"40"}, "body":{ "action": "1" }}


def on_message(ws, message):
     print("----------------------------------")
     print("| message received to client!    |")
     print("----------------------------------")
     secureMSG = SecureMessage()
     try:
        decrypted = secureMSG.decrypt(message).decode("utf-8", "ignore")
        json_loads = json.loads(decrypted)
        if is_json(decrypted):
            print("Action:")
            print(json_loads["body"]["action"])
            print("Hardware:")
            print(json_loads["header"]["hardware_id"])
            print("Tab:")
            print(json_loads["header"]["tab_id"])
            print("........................................")
            if json_loads["header"]["msg_type"] == "ping pong":
              msg["header"]["msg_type"] = "ping pong"
              msg["header"]["sensor_id"] = json_loads["header"]["sensor_id"]
              msg["header"]["tab_id"] = json_loads["header"]["tab_id"] # DONT FORGET TO ADD IT ON THE HARDWARE
              msg["body"]["action"] = "pong"
              print(json_loads["header"]["sensor_id"])
              print("----------------------------------")
              print("| Ping -> received from dashboar |")
              print("----------------------------------")
              json_msg = json.dumps(msg)
              encryptedMSG = secureMSG.enc(json_msg)
              ws.send(encryptedMSG)
              print("----------------------------------")
              print("|  Pong -> send                  |")
              print("----------------------------------")
              print("Action:")
              print(msg["body"]["action"])
              print("Hardware:")
              print( msg["header"]["hardware_id"])
              print("Tab:")
              print( msg["header"]["tab_id"])
              print("........................................")
            elif json_loads["header"]["msg_type"] == "controll":
              msg["header"]["msg_type"] = "verification"
              msg["header"]["sensor_id"] = json_loads["header"]["sensor_id"]
              if json_loads["body"]["action"] == "on":
                print('Relay 1 On')
                msg["body"]["action"] = "started"
              elif json_loads["body"]["action"] == "off":
                print('Relay 1 Off')
                msg["body"]["action"] = "stoped"
              json_verify_msg= json.dumps(msg)
              encryptedVerifyMSG = secureMSG.enc(json_verify_msg)
              ws.send(encryptedVerifyMSG)
            elif json_loads["body"]["action"] == "save":
              print("| Received schedule to save |")
              with open("/home/client/data.json", "w") as doc:
                  json.dump(json_loads, doc, indent=2)
                  print("Json file saved.")
            elif json_loads["body"]["action"] == "profile":
              with open("/home/client/user_profile.json", "w") as doc:
                 json.dump(json_loads, doc, indent=2)
                 print("User profile file saved.")
                 msg["header"]["msg_type"] = "profile save done"
                 msg["header"]["action"] = "profile"
                 msg["header"]["sensor_id"] = 'null'
                 msg["body"]["action"] = "profile"
                 msg["header"]["hardware_id"] = json_loads["header"]["hardware_id"]
                 json_profile = json.dumps(msg)
                 encryptedJsonProfile = secureMSG.enc(json_profile)
                 ws.send(encryptedJsonProfile)
                 print("-------------------------------------")
                 print("Profile data saved. Message send back!")
                 print("--------------------------------------")
            elif json_loads["body"]["action"] == "synch":
              print("-----------------------------------")
              print("| Synch -> received from dashboar |")
              print("-----------------------------------")
              msg["header"]["msg_type"] = "synch started"
              msg["header"]["action"] = "synch"
              msg["header"]["sensor_id"] = json_loads["header"]["sensor_id"]
              msg["header"]["hardware_id"] = json_loads["header"]["hardware_id"]
              json_synch_started = json.dumps(msg)
              encryptedJson_synch_started = secureMSG.enc(json_synch_started)
              ws.send(encryptedJson_synch_started)
              print("-----------------------------------")
              print("| Synch -> started from the client |")
              print("-----------------------------------")
              threading.Thread(target=run_synch, args=(ws, json_loads["header"]["sensor_id"], json_loads["header"]["hardware_id"], secureMSG, msg), daemon=True).start()
            else:
              print(json_loads)
        else: 
           print("--------------------------------------")
           print("|  Client received non json message! |")
           print("|  No action will occur!             |")
           print("|  Message received!                 |")
           print("|", message,                        "|")
           print("--------------------------------------")
     except Exception as e:
        print("Exception type:", type(e).__name__)
        print("Exception message:", str(e))
        print("------------------------------------------------------------------")
        print("|  Decryption was not done                                       |")
        print("|  Pong not send!, it can be wrong decryption key or password!   |")
        print("|  No action will occur!                                         |")
        print("-------------------------------------------------------------------")

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connected client 1")
    
def is_json(myjson):
       try:
            json.loads(myjson)
       except ValueError as e:
            return False
       return True
#Function to synchronise dailyschedule with the database
def run_synch(ws, sensor_id, hardware_id, secure_msg, msg):
    process = subprocess.Popen(['python3', '/home/client/synchronise.py'])
    logger.info(process)
    process.wait()
    print("-----------------------------------")
    print("| Synch -> synch ended             |")
    print("-----------------------------------")
    msg["header"]["msg_type"] = "synch ended"
    msg["header"]["action"] = "synch"
    msg["header"]["sensor_id"] = sensor_id
    msg["header"]["hardware_id"] = hardware_id
    json_synch_ended = json.dumps(msg)
    encryptedJson_synch_ended = secure_msg.enc(json_synch_ended)
    ws.send(encryptedJson_synch_ended)
    

def run():
    while True:
        try:
            ws = websocket.WebSocketApp(
                SERVER_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )

            # This will block until the connection closes or fails
            ws.run_forever(ping_interval=30, ping_timeout=10, reconnect=0)

        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print("Unexpected error:", e)

        # Try to reconnect quickly
        print(f"Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    run()
