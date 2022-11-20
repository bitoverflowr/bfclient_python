import json
class Client:

  def __init__(self,clientname,details):
    self.name = clientname
    self.details  = details
  
  def passer(self):
    return { "name" : self.name , "details" : self.details }
  
  def acknowledge(self,data):
     self.name =  data["name"]
     self.details =  data["details"] 
     
  def connected_server(self, clt):
    self.clientobject = clt
    
  def getdisplayname(self):
    try:
      return self.name
    except:
      return "Unnamed"
  