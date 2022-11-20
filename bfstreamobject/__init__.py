from .. import bfobject as Object


class Stream:
  def __init__(self,client=None,server=None):
    self.server = server
    self.client = client
  
  
  def create(self,source,destination,command,startdata,responsecommand):
     self.streamid = None
     self.source = source
     self.destination = destination
     self.command = command
     self.startdata = startdata
     self.responsecommand = responsecommand
     self.serverack = False
     self.sourceack = False

  
  def Assign(self,streamid):
    self.streamid = streamid
  
  def format(self):
    response = {}
    
    if self.streamid != None:
      response['streamid'] = self.streamid
      
    response["source"] : self.source
    response["destination"] : self.destination
    response["command"] : self.command
    response["data"] : self.startdata
    response["responsecommand"] : self.responsecommand
                
    return response
    
    
  def format_for_streams(self):
    response = {
                "streamid" : self.streamid,
                "source" : self.source,
                "destination" : self.destination,
                "command" : self.command,
                "responsecommand" : self.responsecommand
                }
    return response
    
  def push(self,data):
    obj = Object.Object()
    packet = {"stream" : self.format_for_streams() , "data" : data} 
    obj.create(self.destination,"ceo","response","stream", packet)
    self.client.send(obj.format())
    
  def ServerAcknowledge(self):
    pass
  
  def SourceAcknowledge(self):
    pass
  