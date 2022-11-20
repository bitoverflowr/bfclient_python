import json
import random
class Object:
  responseObject = None

  def __init__(self,manager=None):
      self.manager = manager  
  

  def create(self,source,destination,command,type, data ):
    self.source = source
    self.destination = destination
    self.command = command
    self.type = type
    self.data = data
    self.DuplicationErrorRandomNumber =  random.randint(0,999999999999999)
    self.responded = False


    
  def format(self):
    communicate = { "source" : self.source,
                    "destination" : self.destination ,
                    "command" : self.command ,
                    "type" : self.type,
                    "data" : self.data ,
                    "duplicateerror" : self.DuplicationErrorRandomNumber
                    }

    return json.dumps(communicate)
    
  def loads(self,string):
     jsondata = json.loads(string)
     self.source = jsondata['source']
     self.destination = jsondata['destination']
     self.command = jsondata['command']
     self.type = jsondata['type']
     self.data = jsondata['data']
     self.responsedata = None
     self.DuplicationErrorRandomNumber = jsondata['duplicateerror']
     

     



  def Response(self,data, command = "response" , type = "ot-resp"):
    responseobj = Object(self.manager)
    responseobj.create(self.destination , self.source ,command ,type , data )
    self.responseObject = responseobj
    self.responded = True
    self.manager.tui.log("Adding response for " + self.type)



  def IN_DATA(self):
    return json.dumps(self.data)


  
     
     
     
