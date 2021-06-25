from . import bfobject as Object
from . import bfstreamobject as StreamObject

class SFClient:
  currentconnections = []
  
  def __init__(self, conn):
    self.conn = conn

  def StreamRequestObject(self,source,destination,command,data, fname):
    obj = Object.Object()
    data = { "source" : source , "destination" : destination , "command" : command , "data" : data , "responsecommand" : fname}
    obj.create(source , "ceo" , "streaminit" ,  "stream" , data )
    return obj
 
  def NewStream(self,obj):
     stream = StreamObject.Stream(client = self.conn)
     stream.create(obj['streamid'],obj['source'],obj['destination'],obj['command'],obj['data'],obj['responsecommand'])
     self.currentconnections.append(stream)
     return stream
     
  



  
