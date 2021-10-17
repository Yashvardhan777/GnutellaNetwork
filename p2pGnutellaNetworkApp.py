import time
import pathlib
from config import allToAllTopology, connectPeerSuperPeer, startPeers, startSuperPeers, display, stopPeers, stopSuperPeers
dir = str(pathlib.Path().resolve())

superPeers = startSuperPeers()
peers = startPeers()

time.sleep(5)

allToAllTopology(superPeers)

time.sleep(5)

connectPeerSuperPeer(superPeers, peers)

time.sleep(5)

display(superPeers, peers)

peerId = int(input("Enter the target peer ID: "))
fileName = input("Enter the file you want: ")
superPeerId = str(peerId // 10)
peerNum = str(peerId % 10)

for superPeer in superPeers:
    if superPeer.id == superPeerId:
        targetPeer = superPeer
        targetPeer.requestingPeer = peerNum
        targetPeer.requestingFileName = fileName
        break

sources = set()
for superPeer in targetPeer.all_nodes():
    for i in range(1):
        id = int(superPeer.id)
        if id< 9 and (fileName in superPeers[id - 1].files[i]):
            sources.add((id, superPeers[id - 1], dir + "\\files\\group{0}\\peer{1}\\".format(id, i+1) + fileName))

print("Available Peers:")
for id, x, y in sources:
    print(id, x.port)

tempId = int(input("Enter the ID: "))
for id, x, y in sources:
    if id == tempId:
        sourcePeer = x 
        sourceFile = y 
        break

with open(sourceFile, "r") as f:
    while True:
    
        bytes_read = f.read()
        if not bytes_read:
            f.close()
            break
    
        sourcePeer.send_to_node(n = targetPeer, data = bytes_read)

time.sleep(5)

stopPeers(peers)

time.sleep(20)

stopSuperPeers(superPeers)

time.sleep(20)

print("Terminating ...")