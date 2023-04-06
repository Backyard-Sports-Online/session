# Backyard Sports Online Session Server

This is a Python-based server used to help establish peer-to-peer communication between two clients.

This repository has been deprecated in favor of [ScummVM's new session server](https://github.com/scummvm/scummvm-sites/tree/multiplayer).

# Setup
```
# Install depdendencies
pip install -r requirements.txt

# Run the server
python3 main.py
```

## Test clients
```
# Host a session
python3 client.py 0

# Join a session
python3 client.py <session id given by the host client>
```

## Building a docker image
For the session server:
```
docker build --target main -t session-main:latest .
```
And for a test client:
```
docker build --target client -t session-client:latest .
```
