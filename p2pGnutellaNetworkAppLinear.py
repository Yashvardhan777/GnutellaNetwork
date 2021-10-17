import time
import pathlib
from config import linearTopology, connectPeerSuperPeer, startPeers, startSuperPeers, display, stopPeers, stopSuperPeers
dir = str(pathlib.Path().resolve())


superPeers = startSuperPeers()
peers = startPeers()


def findSource(superPeer, fileName):
    for i in range(1):
        if fileName in superPeers[int(superPeer.id) - 1].files[i]:
            sourcePeer = superPeer
            return sourcePeer

    if superPeer.id == 8:
        return "FileNotFound"

    sourcePeer = findSource(superPeers[int(superPeer.id)], fileName)
    return sourcePeer



time.sleep(5)

linearTopology(superPeers)

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

nextPeer = [peer for peer in targetPeer.all_nodes() if int(peer.id) < 9][0]
sourcePeer = findSource(nextPeer, fileName)

if sourcePeer == "FileNotFound":
    print("File not available")

else:
    sourcePeer.connect_with_node(targetPeer.host, targetPeer.port)
    sourceFile = dir + "\\files\\group{0}\\peer1\\".format(sourcePeer.id) + fileName
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

print("The End")