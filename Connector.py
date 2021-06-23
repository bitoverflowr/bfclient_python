import websocket
import json
import time
import sys

from threading import Thread
from threading import Event
import bitoverflow_object
from bitoverflow_client_python import StreamFlow
from bitoverflow_client_python import BuiltMethods
from inspect import getmembers, isfunction

class ct:
  get_result = None
  result_available = Event()
  status = False
  
  def __init__(self,client,current_module):
     self.client = client
     self.current_module = sys.modules[current_module]
     self.sf = StreamFlow.SFClient(conn=self);
     websocket.enableTrace(False)
     self.ws = websocket.WebSocketApp("ws://localhost:8000",
            on_open=self.on_open,on_message=self.on_message,on_error=self.on_error,on_close=self.on_close)
     
     self.bg = Thread(target = self.run) 
     self.bg.setDaemon(True)
     self.bg.start()
     
     
     

  
  def run(self):
    while True:
      self.ws.run_forever()
      time.sleep(2)
      print("Retrying")
  
  def on_message(self,ws, message):
    #print(message)
    obj = Object.Object()
    obj.loads(message)
    builtfunctions = getmembers(BuiltMethods, isfunction)
    for function in builtfunctions:
      name,address = function
      if obj.command == name:
        getattr(BuiltMethods, name)(self,obj)
        break
    else:  
      if obj.resptype == "onetime":  
         responsedata = getattr(self.current_module, obj.command)(obj.requestdata)
         backobj = Object.Object()
         backobj.create(obj.destination , obj.source , "response" ,  "onetime" , responsedata)
         self.send(backobj.format())
      elif obj.resptype == "stream":
         pass
    

  def on_error(self,ws, error):
    print(error)

  def on_close(self,ws, close_status_code, close_msg):
    print("### closed ###")

  def on_open(self,ws):
    print ("Connected to server - Acknowledgeing")
    self.acknowledge()
    

  def acknowledge(self):
    print ("Connected to server - Acknowledgement Sent")
    obj = Object.Object()
    obj.create(self.client.name , "ceo" , "acknowledge" ,  "onetime" , self.client.passer())
    self.send(obj.format())
    
  def get(self,destination,command,data):
    obj = Object.Object()
    obj.create(self.client.name , destination , command ,  "onetime" , data)
    print("Requesting " + command)
    self.send(obj.format())
    self.result_available.wait()
    res = self.get_result
    self.get_result = None
    self.result_available = Event()
    return res

  def getstream(self,destination,command,data,fname):
    print("Createing stream initiate request")
    obj = self.sf.StreamRequestObject(self.client.name,destination,command,data,fname)
    print("Requesting stream " + command)
    self.send(obj.format())

  def send(self,data):
    #print("Sending data " + data )
    self.ws.send(data)



  def exit(self):
     self.bg.join()











