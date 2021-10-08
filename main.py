import enet
import json

host = enet.Host(enet.Address(b"0.0.0.0", 9130), peerCount=4095, channelLimit=1)

print("Listening for messages on port 9130")

session_counter = 0
# {sessionId: peer}
sessions = {}

tunnel_counter = 0
# {sessionId: peer}
tunnels = {}

# {peer: peer}
relays = {}

debug = 0

def print_debug(*args):
    if debug:
        print(*args, flush=True)

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

        if event.peer in relays:
            # Disconnect their relaying peer.
            dest_peer = relays[event.peer]
            dest_peer.disconnect()
            del relays[event.peer]
            if dest_peer in relays:
                del relays[dest_peer]
    elif event.type == enet.EVENT_TYPE_RECEIVE:
        print_debug("%s: IN:  %r" % (event.peer.address, event.packet.data))

        if event.peer in relays:
            # Relay this packet to their peer
            relays[event.peer].send(0, event.packet)
            continue
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
                print(f'{event.peer.address} attempted to join session {session}, but not on sessions!', flush=True)
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
        elif command == 'host_relay':
            tunnel_counter += 1
            tunnels[tunnel_counter] = event.peer

            send(event.peer, {
                'cmd': 'relay_resp',
                'tunnel': tunnel_counter,
            })
        elif command == 'join_relay':
            tunnel = data.get('tunnel')
            if not tunnel:
                print_debug('join_relay is missing tunnel!')
                continue
            host_peer = tunnels.get(tunnel)
            if not host_peer:
                print(f'{event.peer.address} attempted to join tunnel {tunnel}, but not on tunnels!', flush=True)
                continue

            relays[host_peer] = event.peer
            relays[event.peer] = host_peer

            send(host_peer, {'cmd': 'relay_join'})
            send(event.peer, {'cmd': 'relay_join'})
