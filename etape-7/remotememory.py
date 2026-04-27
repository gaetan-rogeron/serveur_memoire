import socket
import time

MAXBYTES = 8192 # les pages hex sont lourdes, on augmente

class RemoteMemory:
    def __init__(self, host, port, segname, size, debug=False, alloc=True, pagesize=10, cachesize=50):
        self.host, self.port = host, port
        self.segname, self.size = segname, size
        self.pagesize, self.cachesize = pagesize, cachesize
        self.with_debug, self.alloc = debug, alloc
        
        self.cache = bytearray(cachesize) # memoire local
        self.page_table = {} # { page_num: {"offset": int, "dirty": bool, "last_used": float} }
        
        if alloc:
            self.request(f"PUT {self.segname} {self.size} {self.pagesize}")

    def request(self, req):
        # Ajout du \n pour les blocages de sys.stdin
        if not req.endswith("\n"): req += "\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall(req.encode())
        resp = s.recv(MAXBYTES).decode().strip()
        s.close()
        return resp

    def _get_free_offset(self):
        # si le cache n'est pas plein on prend l'offset suivant
        used_offsets = [p["offset"] for p in self.page_table.values()]
        for i in range(0, self.cachesize, self.pagesize):
            if i not in used_offsets: return i
        
        # sinon LRU
        lru_page = min(self.page_table, key=lambda k: self.page_table[k]["last_used"])
        info = self.page_table[lru_page]
        
        if info["dirty"]:
            # On sauvegarde la page modifiee sur le serveur avant de l'effacer
            data = self.cache[info["offset"]:info["offset"] + self.pagesize].hex()
            self.request(f"POST {self.segname} {lru_page} {data}")
            
        offset = info["offset"]
        del self.page_table[lru_page]
        return offset

    def _load_page(self, page_num):
        offset = self._get_free_offset()
        # On recupere la page en hex depuis le serveur
        hex_data = self.request(f"GET {self.segname} {page_num}")
        self.cache[offset:offset + self.pagesize] = bytearray.fromhex(hex_data)
        self.page_table[page_num] = {"offset": offset, "dirty": False, "last_used": time.time()}

    def __getitem__(self, index):
        page_num = index // self.pagesize
        offset_in_page = index % self.pagesize
        
        if page_num not in self.page_table:
            self._load_page(page_num)
        
        info = self.page_table[page_num]
        info["last_used"] = time.time()
        return self.cache[info["offset"] + offset_in_page]

    def __setitem__(self, index, value):
        page_num = index // self.pagesize
        offset_in_page = index % self.pagesize
        
        if page_num not in self.page_table:
            self._load_page(page_num)
        
        info = self.page_table[page_num]
        info["last_used"] = time.time()
        info["dirty"] = True # On marque la page comme modifiee
        self.cache[info["offset"] + offset_in_page] = value

    def flush(self):
        # On ecrit toutes les pages modifiees sur le serveur
        for page_num, info in self.page_table.items():
            if info["dirty"]:
                data = self.cache[info["offset"]:info["offset"] + self.pagesize].hex()
                self.request(f"POST {self.segname} {page_num} {data}")
                info["dirty"] = False

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush() # sauvegarde avant de quitter
        if self.alloc:
            self.request(f"DELETE {self.segname}")
            
    def __len__(self):
        return self.size

    def free(self):
        self.__exit__(None, None, None)