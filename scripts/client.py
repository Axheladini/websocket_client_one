import os
import json
import jsonpickle
import datetime
import queue
import asyncio
import websocket
from websocket import create_connection
from termcolor import colored
import requests
from urllib.error import HTTPError
import urllib.request
import http.client
import ssl
import asyncio
import threading
import _thread
import rel
import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from enc import SecureMessage
try:
    import thread
except ImportError:
    import _thread as thread
import time
import cProfile


msg = { "header":{ "from": "user-3", "from_type": "device", "to": "user-3", "to_type": "vue", "msg_type": "pong", "hardware_id": "43", "sensor_id":"35"}, "body":{ "action": "1" }}

def on_message(ws, message):
     print("----------------------------------")
     print("| message received to client!    |")
     print("----------------------------------")
     secureMSG = SecureMessage()
     try:
        decrypted = secureMSG.decrypt(message).decode("utf-8", "ignore")
        json_loads = json.loads(decrypted)
        print("Is decrypted!")
        print(is_json(decrypted))
        print(json_loads["header"]["to"])
        print(json_loads["body"]["action"])
        print("-------------------------------")
        if is_json(decrypted):
            if json_loads["header"]["msg_type"] == "ping pong":
              msg["header"]["msg_type"] = "ping pong"
              msg["body"]["action"] = "pong"
              print("----------------------------------")
              print("| Ping -> received from dashboar |")
              print("----------------------------------")
              json_msg = json.dumps(msg)
              encryptedMSG = secureMSG.enc(json_msg)
              ws.send(encryptedMSG)
              print("----------------------------------")
              print("|  Pong -> send                  |")
              print("----------------------------------")
            elif json_loads["header"]["msg_type"] == "controll":
              print("controll")
              print(json_loads["body"]["action"])
              msg["header"]["msg_type"] = "verification"
              if json_loads["body"]["action"] == "on":
                msg["body"]["action"] = "started"
              elif json_loads["body"]["action"] == "off":
                msg["body"]["action"] = "stoped"
              json_verify_msg= json.dumps(msg)
              encryptedVerifyMSG = secureMSG.enc(json_verify_msg)
              ws.send(encryptedVerifyMSG)
            elif json_loads["body"]["action"] == "save":
              print("| Received schedule to save |")
              with open('data.json', 'w') as doc:
                   json.dump(json_loads, doc, indent=2)
              print("Json file saved!")
            else:
              print(json_loads)
        else: 
           print("--------------------------------------")
           print("|  Client received non json message! |")
           print("|  No action will occur!             |")
           print("|  Message received!                 |")
           print("|", message,                        "|")
           print("--------------------------------------")
     except:
        print("------------------------------------------------------------------")
        print("|  Decryption was not done                                        |")
        print("|  Pong not send!, it can be wrong decryption key or password!   |")
        print("|  No action will occur!                                          |")
        print("-------------------------------------------------------------------")

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection client 1")

def is_json(myjson):
       try:
            json.loads(myjson)
       except ValueError as e:
            return False
       return True

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://nginx/ws/?id=user-3&type=device&hardware=43",
                              on_open=on_open,
                              on_message=on_message,                                                                                                                                                                                                  on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
