import enet
import json

host = enet.Host(enet.Address(b"0.0.0.0", 9130), peerCount=4095, channelLimit=1)

print("Listening for messages on port 9130")

session_counter = 0
# {sessionId: peer}
sessions = {}

debug = 0

def print_debug(*args):
    if debug:
        print(*args)

def send(peer, data):
    print_debug('sending:', data)
    data = json.dumps(data).encode()
    peer.send(0, enet.Packet(data))

while True:
    event = host.service(1000)
    if event.type == enet.EVENT_TYPE_CONNECT:
        print_debug("%s: CONNECT" % event.peer.address)
    elif event.type == enet.EVENT_TYPE_DISCONNECT:
        print_debug("%s: DISCONNECT" % event.peer.address)
        for session, peer in sessions.items():
            if peer == event.peer:
                del sessions[session]
                break
    elif event.type == enet.EVENT_TYPE_RECEIVE:
        print_debug("%s: IN:  %r" % (event.peer.address, event.packet.data))
        try:
            data = json.loads(event.packet.data)
        except:
            print_debug('Received non-JSON data!')
            continue
        command = data.get('cmd')
        if not command:
            continue

        if command == 'host_session':
            session_counter += 1
            sessions[session_counter] = event.peer

            send(event.peer, {
                'cmd': 'host_resp',
                'session': session_counter,
                'host': event.peer.address.host,
                'port': event.peer.address.port
            })
        elif command == 'join_session':
            session = data.get('session')
            if not session:
                print_debug('join_session is missing session!')
                continue
            host_peer = sessions.get(session)
            if not host_peer:
                print_debug(f'{event.peer.address} attempted to join session {session}, but not on sessions!')
                continue
            send(host_peer, {
                'cmd': 'peer_join',
                'host': event.peer.address.host,
                'port': event.peer.address.port
            })
            send(event.peer, {
                'cmd': 'join_resp',
                'host': host_peer.address.host,
                'port': host_peer.address.port,

                'host_port': event.peer.address.port
            })
