import sys
import cpu
from typing import List

def pyemu_run(argv: List[str] = None)-> int:
    emu = cpu.Cpu()
    if(len(argv) > 1):
        emu.dram.load_bin(dram_bin_path=argv[1])
    emu.run()

if __name__ == "__main__":
    sys.exit(pyemu_run(argv=sys.argv))