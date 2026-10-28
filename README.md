# Client-server file sharing

A TCP file-sharing system in Python. Clients upload files as open or protected, list the files they
can see, and download them, with an MD5 check on every transfer.

Networks assignment, University of Cape Town, 2023. Group of 3; this repo holds the shared server and
my client.

## Features

- Upload a file as **open** (anyone can download it) or **protected** (needs the owner's key)
- List the open files, or the protected files you own
- Download with an integrity check: the MD5 hash of the received bytes must match the server's
- Validation of every command and input on the client side

The server handles one client connection at a time.

## Run

Start the server, then a client in a second terminal:

```bash
python3 server.py
python3 client.py
```

The server listens on `127.0.0.1:4000`; change `IP` and `Port` at the bottom of `server.py` to accept
clients on other machines. The client asks for the server's IP, port and your key, then for a command:
upload, list or download.
