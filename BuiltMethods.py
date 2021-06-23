
def renzvosAcknowledgeResponse(conn,data):
  print("Recieved renzvos Acknowledgement - " + data.requestdata['status'])
  if data.requestdata['status'] == "success":
    conn.status = True
    try:
      getattr(conn.current_module, "connection_is_ready")()
    except:
      pass


def streaminit(conn,data):
    print("Stream initiated")
    stream = conn.sf.NewStream(data.requestdata)
    getattr(conn.current_module, stream.command)(stream.startdata,stream)
 
  
def response(conn,obj):
   if obj.resptype == "onetime":
        print("Recieving one-time response")
        conn.get_result = obj.requestdata
        conn.result_available.set()
   elif obj.resptype == "stream":
        print("Recieving stream")
        getattr(conn.current_module, obj.responsecommand)(obj.requestdata)
        
