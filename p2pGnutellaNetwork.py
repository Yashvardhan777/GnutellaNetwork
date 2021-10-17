from node import Node
import pathlib
from os import listdir
from os.path import isfile, join
class GnutellaNetworkNode (Node):

    
    def __init__(self, host, port, id=None, callback=None, max_connections=0, file=None):
        super(GnutellaNetworkNode, self).__init__(host, port, id, callback, max_connections)
        if file is None:
            self.files = []
        else:
            self.files = file
        self.requestingPeer = -1
        self.requestingFileName= ""
        

    def outbound_node_connected(self, node):
        print("connection made between : (" , self.port , "): " , node.port)
        
    def inbound_node_connected(self, node):
        print("connection made between : (" , self.port , "): " , node.port)

    def inbound_node_disconnected(self, node):
        print("connection made between : (" , self.port , "): " , node.port)

    def outbound_node_disconnected(self, node):
        print("connection made between : (" , self.port , "): " , node.port)

    def node_message(self, node, data):
        print("node_message (" , self.id, ") from",  node.id , ": " , str(data))
        dir = str(pathlib.Path().resolve())
        path = dir + "\\files\\group{0}\\peer{1}".format(self.id, self.requestingPeer)
    
        targetFile = path + "\\" + self.requestingFileName
        with open(targetFile, "w") as f:
            try:
                f.write(str(data))
            except Exception as e:
                print(e)
                f.close()
                return
           
    def node_disconnect_with_outbound_node(self, node):
        print("node wants to disconnect with oher outbound node: (" , self.port , "): " , node.port)
        
    def node_request_to_stop(self):
        print("node is requested to stop (" , self.port , "): ")
        
