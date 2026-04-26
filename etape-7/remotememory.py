import socket

MAXBYTES = 1024

class RemoteMemory:
    def __init__(self, host, port, segname, size, debug=False, alloc=True):
        self.host = host
        self.port = port
        self.segname = segname
        self.size = size
        self.with_debug = debug
        self.alloc = alloc
        if alloc:
            self.request(f"PUT {self.segname} {self.size}")

    def __enter__(self):
        return self

    def request(self, request):
        self.debug(f"Creating socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug(f"Connecting to remote memory at {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        self.debug(f"Connected")
        self.debug(f"Sending request: '{request}'")
        self.socket.sendall(request.encode())
        responses = self.socket.recv(MAXBYTES).decode().strip().splitlines()
        for response in responses:
            response = response.strip()
            if response.startswith("[debug]"):
                if self.with_debug:
                    self.debug(f"[from server] {response[8:]}")
                else:
                    continue
            else:
                self.debug(f"Received response: '{response}'")
                self.socket.close()
                if response.startswith("error"):
                    raise ValueError(f"error from remote memory: {response}")
                return response

    def debug(self, message):
        if self.with_debug:
            print(f"[debug] {message}")

    def __getitem__(self, index):
        response = self.request(f"GET {self.segname} {index}")
        return int(response)
    
    def __setitem__(self, index, value):
        self.request(f"POST {self.segname} {index} {value}")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.alloc: # modif pour 6.3
            self.request(f"DELETE {self.segname}")

    def __len__(self):
        return self.size
    
    def free(self):
        if self.alloc:
            self.request(f"DELETE {self.segname}")