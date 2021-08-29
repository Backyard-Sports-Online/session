# Backyard Sports Online Session Server

This is a Python-based server used to help establish peer-to-peer communication between two clients.

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
