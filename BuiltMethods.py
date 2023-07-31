from . import bfobject as Object

def renzvosAcknowledgeResponse(connection,obj):
  if connection.log_ack :print("Recieved renzvos Acknowledgement - " + obj.data['status'])
  if obj.data['status'] == "success":
    connection.connected = True
  if obj.data['status'] == "fail":
    if obj.data["detail"] == "client-exists":
      connection.client_exist_callback = True


def close_waiting(conn , result):
  if conn.waiting == True:
       conn.get_result = result
       conn.waiting = False
       conn.result_available.set()

def Incoming_Stream_Request(conn,obj):
    print("Recieved Stream Request")
    for fun in conn.callbacks:
        if fun["command"] == obj.command and fun["type"] == "st-init":
          details = {"status" : "success"}
          resp_obj = Object.Object()
          resp_obj.create(conn.client.name , obj.source , obj.command , "st-init-resp" , details)
          conn._send(resp_obj)
          fun["callback"](conn , obj.source , obj.data)


def Incoming_Stream_init_response(conn,result):
    print("Stream-init Response Recieved")
    close_waiting(conn,result)
       


def one_time_request_handle(conn,obj):
    print("One Time Request Incoming")
    for details in conn.callbacks:
       if details["command"] == obj.command and details["type"] == "ot":
          response = details["callback"](obj, obj.source , obj.data)
          resp_obj = Object.Object()
          resp_obj.create(conn.client.name , obj.source , obj.command , "ot-resp" , response)
          conn._send(resp_obj)
  

        

def one_time_response(conn, obj):
    print("Response Recieved")
    close_waiting(conn,obj)
       

def noclient(conn,obj):
  print("Expected Client not availible")
  close_waiting(conn, obj)


def stream_object(conn,obj):
   for fun in conn.callbacks:
        if fun["command"] == obj.command and fun["type"] == "st":
          fun["callback"](conn , obj.source , obj.data )

def stream_end_object(conn,obj):
  print("Got End object")
  for fun in conn.callbacks:
      if fun["command"] == obj.command and fun["type"] == "st":
          if fun["waiting"]:
              print("It is waiting")
              close_waiting(conn,obj)
          fun["onEnd"](conn , obj.source , obj.data )


