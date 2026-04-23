class ControledMemory:
    def __init__(self, memory):
        self.size = len(memory)
        self.memory = memory
        self.control = [None] * self.size

    def __enter__(self):
        return self

    def __getitem__(self, index):
        v1 = self.memory[index]
        v2 = self.control[index]
        if v1 != v2:
            if v2 is None:
                self.control[index] = v1
            else:
                raise ValueError(f"Memory corruption detected at index {index}: expected {v2}, got {v1}")
        return v1

    def __setitem__(self, index, value):
        self.memory[index] = value
        self.control[index] = value

    def __len__(self):
        return self.size
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.memory.__exit__(exc_type, exc_value, traceback)