import sys
import pathlib
from os import listdir
from os.path import isfile, join
from p2pGnutellaNetwork import GnutellaNetworkNode

host = 'localhost'

def startSuperPeers():
    superPeers = []
    port =  1001
    for i in range(1,9):
        superPeers.append(GnutellaNetworkNode(host, port,id=str(i), max_connections=9))
        port += 1
        superPeers[-1].start()
    return superPeers


def startPeers():
    peers = []
    port = 3001
    dir = str(pathlib.Path().resolve())

    for i in range(1,9):
        temp = []
        for j in range(1,2):
            tempPort = int(str(port) + str(j))
            path = dir + "\\files\\group{0}\\peer{1}".format(i, j)
            temp.append(GnutellaNetworkNode(host, tempPort, id=str(i)+str(j), max_connections=1, file = [f for f in listdir(path) if isfile(join(path, f))]))
            temp[-1].start()
        peers.append(temp)
        port += 1

    return peers 


def allToAllTopology(superPeers):
    for i in range(8):
        for j in range(8):
            superPeers[i].connect_with_node(host, superPeers[j].port)


def linearTopology(superPeers):
    for i in range(7):
        superPeers[i].connect_with_node(host, superPeers[i + 1].port)


def connectPeerSuperPeer(superPeers, peers):
    for i in range(8):
        for j in range(len(peers[i])):
            superPeers[i].connect_with_node(host, peers[i][j].port)
            superPeers[i].files.append(peers[i][j].files)


def display(superPeers, peers):
    print("Network:")
    print("Peers:")
    for group in peers:
        for peer in group:
            print(peer.id, peer.port, "Files:", peer.files)

    print("Super Peers:")
    for superPeer in superPeers:
        print(superPeer.id, superPeer.port)


def stopPeers(peers):
    for i in range(8):
        for j in range(len(peers[i])):
            peers[i][j].stop()

def stopSuperPeers(superPeers):
    for i in range(8):
        superPeers[i].stop()