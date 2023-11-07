import numpy as np
import logging
import dram

class XRegisters():
    def __init__(self) -> None:
        # 32 个 64 位的通用整数寄存器
        self.xregs = [np.uint64(0)] * 32
        self._xnames  = [
            "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
            "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
            "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
            "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6"
        ]
        # sp寄存器初始化
        self.xregs[0] = 0
        self.xregs[2] = np.uint64(dram.DRAM_SIZE - 1)
        

    def read(self, index:int) -> np.uint64:
        if index >=0 and index < 32:
            return self.xregs[index]
        else:
            return None
        
    def write(self, index:int, value:np.uint64):
        if not isinstance(value, np.uint64):
            value = np.uint64(value)
        if index >=0 and index < 32:
            self.xregs[index] = value

    def dump(self):
        print("{:-^110}".format("registers"))
        output = ""
        self.xregs[0] = 0
        for i in range(0, 32, 4):
            i0 = "x{}".format(i)
            i1 = "x{}".format(i + 1)
            i2 = "x{}".format(i + 2)
            i3 = "x{}".format(i + 3)
            line = "{:3}({:^4}) = {:<#18x} {:3}({:^4}) = {:<#18x} {:3}({:^4}) = {:<#18x} {:3}({:^4}) = {:<#18x}\n".format(
                i0, self._xnames[i], self.xregs[i], 
                i1, self._xnames[i + 1], self.xregs[i + 1], 
                i2, self._xnames[i + 2], self.xregs[i + 2], 
                i3, self._xnames[i + 3], self.xregs[i + 3]
            )
            output += line
        print(output)

class Cpu():
    def __init__(self) -> None:
        self.xregs = XRegisters()
        self.pc = np.uint64(0)
        self.dram = dram.Dram()
    
    def fetch(self):
        addr = self.pc
        inst_byte = self.dram.load(int(addr), 4)
        return inst_byte[0] | inst_byte[1] << 8 | inst_byte[2] << 16 | inst_byte[3] << 24
    
    def loadint(self, addr, size):
        arr = self.dram.load(addr, size)
        val = arr
        if isinstance(arr, bytes) or isinstance(arr, bytearray):
            val = int.from_bytes(arr, byteorder='little', signed=True)
        return np.uint64(val)
    
    def execute(self, inst):

        opcode = inst & 0x7f
        rd = (inst >> 7) & 0x1f
        rs1 = (inst >> 15) & 0x1f
        rs2 = (inst >> 20) & 0x1f
        funct3 = (inst >> 12) & 0x7;
        funct7 = (inst >> 25) & 0x7f;

        match opcode:
            # addi(RI)
            case 0x13:
                imm = np.uint64(np.int32(inst&0xfff00000)>>20)
                value = np.uint64(self.xregs.read(rs1) + imm)
                self.xregs.write(rd, value)
            #add(RR)
            case 0x33:
                value = np.uint64(self.xregs.read(rs1) + self.xregs.read(rs2))
                self.xregs.write(rd, value)
            #load
            case 0x03:
                imm = np.uint64((np.int32(inst) >> 20))
                addr = int(self.xregs.read(rs1) + imm)
                val = np.uint64(0)
                match funct3:
                    #lw
                    case 0x2: 
                        val = self.loadint(addr, 4)
                self.xregs.write(rd, val)
            # store
            case 0x23: 
                 imm = np.uint64((np.int32(inst & 0xfe000000) >> 20)) |\
                      np.uint64(((inst >> 7) & 0x1f))
                 addr = int(self.xregs.read(rs1) + imm)
                 value = np.uint64(self.xregs.read(rs2))
                 vbytes = value.tobytes()
                 match funct3:
                     # sw
                     case 0x2:
                         self.dram.store(addr, 4, vbytes[0:8])
            # branch
            case 0x63:
                imm = (np.int32(inst & 0x80000000) >> 19).astype('uint64') |\
                      np.uint64(((inst & 0x80) << 4)) |\
                      np.uint64(((inst >> 20) & 0x7e0)) |\
                      np.uint64(((inst >> 7) & 0x1e))
                cond = False
                match funct3:
                     case 0x0:
                        # beq
                        cond = self.xregs.read(rs1) == self.xregs.read(rs2)
                if cond:
                    self.pc = np.uint64(self.pc + imm - 4)
            # jalr
            case 0x67:
                temp = self.pc
                imm = np.uint64(np.int32(inst & 0xfff00000) >> 20)
                self.pc = (np.uint64(self.xregs.read(rs1) + imm)) & np.uint64(~1)
                self.xregs.write(rd, temp)
            # jal
            case 0x6f:
                self.xregs.write(rd, self.pc)
                imm = np.uint64(np.int32(inst&0x80000000)>>11) |\
                      np.uint64((inst & 0xff000)) |\
                      np.uint64(((inst >> 9) & 0x800)) |\
                      np.uint64(((inst >> 20) & 0x7fe))
                self.pc = np.uint64(self.pc) + np.uint64(imm) - np.uint64(4)
            case _:
                print("UnSupported inst", hex(inst))
                return False
        return True



    def run(self):
        while True:
            inst = self.fetch()
            self.pc +=  np.uint64(4)
            logging.debug(f"pc {hex(self.pc)} {hex(inst)}")
            result = self.execute(inst)
            if not result:
                print("Stop with unknown inst")
                self.xregs.dump()
                break

