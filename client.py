import sys
import enet
import json
import time

client = enet.Host(None, peerCount=4095, channelLimit=1)
session_peer = client.connect(enet.Address(b"127.0.0.1", 9130), 1)

session_loop = True

host_address = None
peer_address = None

def send(peer, data):
    data = json.dumps(data).encode()
    print("%s: OUT:  %r" % (peer.address, data))
    peer.send(0, enet.Packet(data))

while session_loop:
    event = client.service(1000)
    if event.type == enet.EVENT_TYPE_CONNECT:
        print("%s: CONNECT" % event.peer.address)
        session = int(sys.argv[1])
        if session:
            send(session_peer, {'cmd': 'join_session', 'session': session})
        else:
            send(session_peer, {'cmd': 'host_session'})

    elif event.type == enet.EVENT_TYPE_DISCONNECT:
        print("%s: DISCONNECT" % event.peer.address)
        session_loop = False
        continue
    elif event.type == enet.EVENT_TYPE_RECEIVE:
        print("%s: IN:  %r" % (event.peer.address, event.packet.data))

        data = json.loads(event.packet.data)
        command = data['cmd']

        if command == 'host_resp':
            # host = data['host']
            port = data['port']

            host_address = enet.Address(b'0.0.0.0', port)
            print('Our session:', data['session'])
        elif command == 'peer_join':
            host = data['host']
            port = data['port']
            peer_address = enet.Address(host.encode(), port)

            session_peer.disconnect()
        elif command == 'join_resp':
            host = data['host']
            port = data['port']
            peer_address = enet.Address(host.encode(), port)

            host_port = data['host_port']

            session_peer.disconnect()

del session_peer
del client

if not peer_address:
    print('Disconnected without peer address!')
    sys.exit(1)

if host_address:
    server = enet.Host(host_address, peerCount=1, channelLimit=1)
    ping_peer = server.connect(peer_address, 1)

    ping_counter = 0
    while ping_counter < 10:
        print('ping_counter', ping_counter)
        event = server.service(50)
        if event.type == enet.EVENT_TYPE_CONNECT:
            ping_counter = 10
        ping_counter += 1

    ping_peer.disconnect()
    server.flush()

    while True:
        event = server.service(1000)
        if event.type == enet.EVENT_TYPE_CONNECT:
            print("%s: CONNECT" % event.peer.address)
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            print("%s: DISCONNECT" % event.peer.address)
            sys.exit(0)
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            print("%s: IN:  %r" % (event.peer.address, event.packet.data))
            event.peer.send(0, event.packet)

else:
    client = enet.Host(enet.Address(b'0.0.0.0', host_port), peerCount=1, channelLimit=1)
    host_peer = client.connect(peer_address, 1)

    while True:
        event = client.service(1000)
        if event.type == enet.EVENT_TYPE_CONNECT:
            print("%s: CONNECT" % event.peer.address)
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            print("%s: DISCONNECT" % event.peer.address)
            sys.exit(0)
        elif event.type == enet.EVENT_TYPE_RECEIVE:
            print("%s: IN:  %r" % (event.peer.address, event.packet.data))
        elif event.type == enet.EVENT_TYPE_NONE:
            host_peer.send(0, enet.Packet(b'Hello, world!'))
