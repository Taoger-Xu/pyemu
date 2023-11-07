import numpy as np
DRAM_SIZE = 1024 * 1024 * 128

class Dram():
    def __init__(self, dram_bin_path = None, size=0x10000) -> None:
        self.dram = bytearray(size)
        self.size = size
        # dram_bin_path:用来初始化dram的可执行二进制文件的路径
        if dram_bin_path:
            with open(dram_bin_path, 'rb') as f:
                data = f.read()
                data_len = len(data) if len(data) < self.size else self.size
                self.store(0, data_len, data)

    def load_bin(self, dram_bin_path = None):
        with open(dram_bin_path, 'rb') as f:
                data = f.read()
                data_len = len(data) if len(data) < self.size else self.size
                self.store(0, data_len, data)

    def load(self, addr:int, size):
        addr = int(addr)
        return self.dram[addr:addr+size]
        
    def store(self, addr, size, data):
        addr = int(addr)
        if isinstance(data, int) or isinstance(data, np.uint64):
            data = np.uint64(data).tobytes()
        self.dram[addr:addr+size] = data[:size]
        