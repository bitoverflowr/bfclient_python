from . import bfobject as Object

def renzvosAcknowledgeResponse(connection,obj):
  if connection.log_ack :print("Recieved renzvos Acknowledgement - " + obj.data['status'])
  if obj.data['status'] == "success":
    connection.connected = True
  if obj.data['status'] == "fail":
    if obj.data["detail"] == "client-exists":
      connection.client_exist_callback = True



def Incoming_Stream_Request(conn,obj):
    print("Recieved Stream Request")
    for fun in conn.responsefunctions:
        if fun["command"] == obj.command and fun["type"] == "st-init":
          details = {"status" : "success"}
          resp_obj = Object.Object()
          resp_obj.create(conn.client.name , obj.source , obj.command , "st-init-resp" , details)
          conn._send(resp_obj)
          fun["function"](conn , obj.source , obj.data)




def one_time_request_handle(conn,obj):
    print("One Time Request Incoming")
    for details in conn.responsefunctions:
       if details["command"] == obj.command and details["type"] == "ot":
          response = details["function"](obj)
          resp_obj = Object.Object()
          resp_obj.create(conn.client.name , obj.source , obj.command , "ot-resp" , response)
          conn._send(resp_obj)
  

        

def one_time_response(conn, obj):
   if conn.waiting == True:
       print("Response Recieved")
       conn.get_result = obj.data
       conn.waiting = False
       conn.result_available.set()
       

def noclient(conn,obj):
   if conn.waiting == True:
       print("Expected Client not availible")
       conn.get_result = {"Error" : "Client not online"}
       conn.waiting = False
       conn.result_available.set()
       

