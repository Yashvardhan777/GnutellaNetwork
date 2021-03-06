import socket
import time
import threading
import random
import hashlib

from nodeconnection import NodeConnection

class Node(threading.Thread):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):    
        super(Node, self).__init__()
        self.terminate_flag = threading.Event()
        self.host = host
        self.port = port
        self.callback = callback
        self.nodesInbound = []  
        self.nodes_outbound = [] 
        self.reconnect_to_nodes = []
        self.id = str(id) 
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()
        self.message_count_send = 0
        self.message_count_recv = 0
        self.message_count_rerr = 0
        self.max_connections = max_connections
        self.debug = False

   
    def all_nodes(self):
        return self.nodesInbound + self.nodes_outbound

    def debug_print(self, message):
        if self.debug:
            print("DEBUG (" , self.id , "): " , message)

    def init_server(self):
        print("Initialisation a leaf node in  port: " + str(self.port) + " on node (" + self.id + ")")
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.soc.bind((self.host, self.port))
        self.soc.settimeout(10.0)
        self.soc.listen(1)

   

    

    def send_to_node(self, n, data):
        self.message_count_send = self.message_count_send + 1
        for node in self.all_nodes():
            if node.id == n.id:
                node.send(data)
                return True
        else:
            print("Node send to node: Could not send the data, node is not found!")
            return False

    def connect_with_node(self, host, port, reconnect=False):
        if host == self.host and port == self.port:
            print("connect with node: Cannot connect with yourself!!")
            return False

        for node in self.nodes_outbound:
            if node.host == host and node.port == port:
                print("connect with node: Already connected with this node (" + node.id + ").")
                return True

        try:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            soc.connect((host, port))

            soc.send(self.id.encode('utf-8'))
            connected_node_id = soc.recv(4096).decode('utf-8')

            for node in self.nodesInbound:
                if node.host == host and node.id == connected_node_id:
                    print("connect with node: This node (" + node.id + ") is already connected with us.")
                    return True

            thread_client = self.create_new_connection(soc, connected_node_id, host, port)
            thread_client.start()

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)

            if reconnect:
                self.debug_print("connect with node: Reconnection check is enabled on node " + host + ":" + str(port))
                self.reconnect_to_nodes.append({
                    "host": host, "port": port, "tries": 0
                })

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")

    def disconnect_with_node(self, node):
        if node in self.nodes_outbound:
            self.node_disconnect_with_outbound_node(node)
            node.stop()
        else:
            self.debug_print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

    def stop(self):
        self.node_request_to_stop()
        self.terminate_flag.set()

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)

    def reconnect_nodes(self):
        for node_to_check in self.reconnect_to_nodes:
            found_node = False
            self.debug_print("reconnect_nodes: Checking node " + node_to_check["host"] + ":" + str(node_to_check["port"]))

            for node in self.nodes_outbound:
                if node.host == node_to_check["host"] and node.port == node_to_check["port"]:
                    found_node = True
                    node_to_check["trials"] = 0 
                    self.debug_print("reconnect_nodes: Node " + node_to_check["host"] + ":" + str(node_to_check["port"]) + " still running!")

            if not found_node: 
                node_to_check["trials"] += 1
                if self.node_reconnection_error(node_to_check["host"], node_to_check["port"], node_to_check["trials"]):
                    self.connect_with_node(node_to_check["host"], node_to_check["port"])

                else:
                    self.debug_print("reconnect_nodes: Removing node (" + node_to_check["host"] + ":" + str(node_to_check["port"]) + ") from the reconnection list!")
                    self.reconnect_to_nodes.remove(node_to_check)

    def run(self):
        while not self.terminate_flag.is_set(): 
            try:
                self.debug_print("Node: Wait for incoming connection")
                connection, client_address = self.soc.accept()

                self.debug_print("Total inbound connections:" + str(len(self.nodesInbound)))
                
                if self.max_connections == 0 or len(self.nodesInbound) < self.max_connections:
                    
                    
                    connected_node_id = connection.recv(4096).decode('utf-8')
                    connection.send(self.id.encode('utf-8')) 

                    thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], client_address[1])
                    thread_client.start()

                    self.nodesInbound.append(thread_client)
                    self.inbound_node_connected(thread_client)

                else:
                    self.debug_print("New connection is closed. You have reached the maximum connection limit!")
                    connection.close()
            
            except socket.timeout:
                self.debug_print('Node: Connection timeout!')

            except Exception as e:
                raise e

            self.reconnect_nodes()

            time.sleep(0.01)

        print("Node stopping...")
        for t in self.nodesInbound:
            t.stop()

        for t in self.nodes_outbound:
            t.stop()

        time.sleep(1)
        self.soc.settimeout(None)   
        self.soc.close()
        print("Node stopped")

    def outbound_node_connected(self, node):
        
        self.debug_print("outbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_connected", self, node, {})

    def inbound_node_connected(self, node):
        self.debug_print("inbound_node_connected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_connected", self, node, {})

    def node_disconnected(self, node):
        self.debug_print("node_disconnected: " + node.id)

        if node in self.nodesInbound:
            del self.nodesInbound[self.nodesInbound.index(node)]
            self.inbound_node_disconnected(node)

        if node in self.nodes_outbound:
            del self.nodes_outbound[self.nodes_outbound.index(node)]
            self.outbound_node_disconnected(node)

    def inbound_node_disconnected(self, node):
        self.debug_print("inbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("inbound_node_disconnected", self, node, {})

    def outbound_node_disconnected(self, node):
        self.debug_print("outbound_node_disconnected: " + node.id)
        if self.callback is not None:
            self.callback("outbound_node_disconnected", self, node, {})

    def node_message(self, node, data):
        self.debug_print("node_message: " + node.id + ": " + str(data))
        if self.callback is not None:
            self.callback("node_message", self, node, data)

    def node_disconnect_with_outbound_node(self, node):
        self.debug_print("node wants to disconnect with oher outbound node: " + node.id)
        if self.callback is not None:
            self.callback("node_disconnect_with_outbound_node", self, node, {})

    def node_request_to_stop(self):
        self.debug_print("node is requested to stop!")
        if self.callback is not None:
            self.callback("node_request_to_stop", self, {}, {})

    def node_reconnection_error(self, host, port, trials):
        self.debug_print("node_reconnection_error: Reconnecting to node " + host + ":" + str(port) + " (trials: " + str(trials) + ")")
        return True

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
