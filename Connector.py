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
  callbacks = []
  on_ready = None
  debug_deep = False
  
  log_ack = False
  log_traffic = False
  log_data = False
  log_status = False

  client_exist_callback = False
  no_server_found_callback = False
  
  def __init__(self,client,current_module  ,retry_count = 3  , log_ack = False , log_traffic = False , log_data = False, log_status=False):
     self.client = client
     self.retry_count = retry_count
     self.current_module = sys.modules[current_module]
     self.log_ack = log_ack
     self.log_data = log_data
     self.log_status = log_status
     self.log_traffic = log_traffic
     self.sf = StreamFlow.SFClient(conn=self)
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
         self.exit()
         raise RuntimeError("Client already exists - Try Another Name")
       if self.no_server_found_callback:
         if self.log_status : print("No Server Found - Retry Finished")
         self.exit()
         raise RuntimeError("No Server Found - Retry Finished")

           
     
     
     

  
  def __run(self):
    while self.switch:
      if self.log_status : print("Connecting to Server")
      self.ws.run_forever()
      self.ws.close()
      if self.switch : time.sleep(2)
      if self.log_status : print(" Retry Counter " + str(self.current_retry_count))
      if  self.current_retry_count >  self.retry_count:
        if self.log_status : print(" Retry Finished ")
        self.no_server_found_callback = True
        break
      self.current_retry_count = self.current_retry_count + 1
    if self.log_status : print("Connection and Background Thread is closed")
      
  
  def __on_message(self,ws, message):
    obj = Object.Object()
    obj.loads(message)
    
    

    if obj.type == "ack-resp":
        if self.log_traffic :  print(self.client.name + ": Incoming Acknowledgement " + obj.type)
        BuiltMethods.renzvosAcknowledgeResponse(self,obj)

    elif obj.type == "no-client":
        if self.log_traffic :  print(self.client.name + ": Incoming No Client Response " + obj.type)
        BuiltMethods.noclient(self,obj)
    
    elif obj.type == "ot-req":
        if self.log_traffic :  print(self.client.name + ": Incoming One-Time Request " + obj.type)
        BuiltMethods.one_time_request_handle(self,obj)
        
    elif obj.type == "ot-resp":  
        if self.log_traffic :  print(self.client.name + ": Incoming One-Time Response " + obj.type)
        BuiltMethods.one_time_response(self,obj)

    elif obj.type == "st-init-req":
      if self.log_traffic :  print(self.client.name + ": Incoming StreamInitiate Request " + obj.type)
      BuiltMethods.Incoming_Stream_Request(self,obj)
    
    elif obj.type == "st-init-resp":
       if self.log_traffic :  print(self.client.name + ": Incoming One-Time Response " + obj.type)
       BuiltMethods.Incoming_Stream_init_response(self,obj)
    
    elif obj.type == "st":
      if self.log_traffic :  print(self.client.name + ": Incoming Stream Object " + obj.type)
      BuiltMethods.stream_object(self,obj)
    
    elif obj.type == "st-end":
      if self.log_traffic :  print(self.client.name + ": Incoming Stream End Object " + obj.type)
      BuiltMethods.stream_end_object(self,obj)
    else:
      if self.log_traffic :  print(self.client.name + ": Incoming Unknown Message " + obj.type)

    if self.log_data :  print(obj.format())
      
  
    

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
    self.callbacks.append( {"command" : command , "type" : "ot" , "callback" : function,} )
  
  def respond_stream(self , command , data , destination = None):
    obj = Object.Object()
    if destination == None : destination = "ceo"
    obj.create(self.client.name , destination , command ,  "st" , data)
    self._send(obj)

  def end_respond_stream(self,command,destination) :
    obj = Object.Object()
    obj.create(self.client.name, destination , command , "st-end" , {"cause" : "source-request"})
    self._send(obj)

  def request_stream(self,destination,command,data, callback  , wait=False , onEnd=None ):
    self.callbacks.append({"command" : command , "type" : "st" , "callback" : callback , "onEnd" : onEnd , "waiting" : wait})
    response = self.___request_with_type(destination,command,data,"st-init-req")
    self.wait()
    return response
  
  def on_stream_start_request(self,command,function):
    self.callbacks.append( {"command" : command , "type" : "st-init" , "callback" : function, } )

  def _send(self,obj : Object.Object):
    #print("Sending data " + data )
    jsonstring = obj.format()
    if self.log_traffic : print(self.client.name + " : Outgoing " + obj.type )
    if self.log_data :  print(jsonstring)
    self.ws.send(jsonstring)
  
  def ___request_with_type(self,destination , command , data , type):
    obj = Object.Object()
    obj.create(self.client.name , destination , command ,  type , data)
    
    self._send(obj)
    res = self.wait()
    if res.type == "no-client":
      self.exit()
      raise RuntimeError("Expected Client is not online")
    return res.data

  def ping(self):
    obj = Object.Object()
    obj.create(self.client.name , "ceo" , "" ,  "ping" , {} )
    if self.log_traffic : print("Requesting ping")
    result = self.request("ceo","ping","{}")
    return result

  def wait(self):
    if self.log_traffic : print(self.client.name +  " : Waiting")
    self.waiting = True
    self.result_available = Event()
    self.result_available.wait()
    res = self.get_result
    self.waiting = False
    self.get_result = None
    if self.log_traffic : print(self.client.name +  " : Wait Finished")
    return res

  def exit(self):
     self.switch = False
     self.ws.keep_running = False 
     self.bg.join()











