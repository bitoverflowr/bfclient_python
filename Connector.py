import websocket
import json
import time
import sys

from threading import Thread
from threading import Event
from . import bfobject as Object
from . import bfclientobject as Client
from . import StreamFlow
from . import BuiltMethods
from inspect import getmembers, isfunction

class ct:
  waiting = False
  get_result = None
  result_available = Event()
  switch = True
  connected = False
  current_retry_count = 0
  responsefunctions = []
  on_ready = None
  debug_deep = False
  client_exist_callback = False
  log_ack = False
  log_traffic = True
  log_data = False
  log_status = False
  
  def __init__(self,client,current_module  ,retry_count = 3 ):
     self.client = client
     self.retry_count = retry_count
     self.current_module = sys.modules[current_module]
     self.sf = StreamFlow.SFClient(conn=self);
     websocket.enableTrace(self.debug_deep)
     self.ws = websocket.WebSocketApp("ws://localhost:8000",
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close)
     
     self.bg = Thread(target = self.__run) 
     self.bg.setDaemon(True)
     self.bg.start()
     while True:
       if self.log_status : print("Waiting for connection")
       time.sleep(0.1)
       if self.connected:
         if self.log_status : print("Connected")
         break
       if self.client_exist_callback:
         if self.log_status : print("Client Exists")
         raise RuntimeError("Client already exists - Try Another Name")
           
     
     
     

  
  def __run(self):
    while self.switch:
      if self.log_status : print("Connecting to Server")
      self.ws.run_forever()
      self.ws.close()
      if self.switch : time.sleep(2)
      if  self.current_retry_count >  self.retry_count:
        break
      self.current_retry_count = self.current_retry_count + 1
    if self.log_status : print("Connection and Background Thread is closed")
      
  
  def __on_message(self,ws, message):
    obj = Object.Object()
    obj.loads(message)
    if self.log_traffic :  print(self.client.name + ": Incoming Message " + obj.type)
    if self.log_data :  print(obj.format())


    if obj.type == "ack-resp":
        BuiltMethods.renzvosAcknowledgeResponse(self,obj)

    if obj.type == "no-client":
        BuiltMethods.noclient(self,obj)
    
    if obj.type == "ot-req":
        BuiltMethods.one_time_request_handle(self,obj)
        
    if obj.type == "ot-resp":  
        BuiltMethods.one_time_response(self,obj)

    if obj.type == "st-init-req":
      BuiltMethods.Incoming_Stream_Request(self,obj)
    
    if obj.type == "st-init-resp":
       
  
    

  def __on_error(self,ws, error):
    print(error)

  def __on_close(self,ws, close_status_code, close_msg):
    print("### closed ###")

  def __on_open(self,ws):
    if self.log_status or self.log_ack : print ("Connected to server - Acknowledgeing")
    self.__acknowledge()
    

  def __acknowledge(self):
    if self.log_ack : print ("Connected to server - Acknowledgement Sent")
    obj = Object.Object()
    obj.create(self.client.name , "ceo" , "" ,  "ack-req" , self.client.passer())
    self._send(obj)
    
  def request(self,destination,command,data):
    return self.___request_with_type(destination,command,data,"ot-req")
  
  def respond(self, command ,  function):
    self.responsefunctions.append( {"command" : command , "type" : "ot" , "function" : function,} )
  
  def respond_stream(self, destination : Client.Client , command , data):
    obj = Object.Object()
    obj.create(self.client.name , destination.name , "response" ,  "stream" , data)
    print("Responding Stream " + command)
    self._send(obj)
    

  def request_stream(self,destination,command,data,on_message):
    response = self.___request_with_type(destination,command,data,"st-init-req")
    return response
  
  def on_stream_start_request(self,command,function):
    self.responsefunctions.append( {"command" : command , "type" : "st-init" , "function" : function, } )

  def _send(self,obj : Object.Object):
    #print("Sending data " + data )
    if self.log_traffic : print(self.client.name + " : Outgoing " + obj.type )
    if self.log_data :  print(jsonstring)
    jsonstring = obj.format()
    self.ws.send(jsonstring)
  
  def ___request_with_type(self,destination , command , data , type):
    obj = Object.Object()
    obj.create(self.client.name , destination , command ,  type , data)
    
    self._send(obj)
    self.waiting = True
    if self.log_traffic : print(self.client.name +  " : Waiting")
    self.result_available = Event()
    self.result_available.wait()
    res = self.get_result
    self.waiting = False
    self.get_result = None
    if self.log_traffic : print(self.client.name +  " : Wait Finished")
    return res

  def ping(self):
    obj = Object.Object()
    obj.create(self.client.name , "ceo" , "" ,  "ping" , {} )
    if self.log_traffic : print("Requesting ping")
    result = self.request("ceo","ping","{}")
    return result



  def exit(self):
     self.switch = False
     self.ws.keep_running = False 
     self.bg.join()











