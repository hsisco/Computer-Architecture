"""CPU functionality"""

import sys

class CPU:
    """Main CPU class"""

    def __init__(self):
        """Construct a new CPU"""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True

        self.index = self.ram[self.pc + 1]
        self.value = self.ram[self.pc + 2]

        self.branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b00000001: self.HLT,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET
        }

        # Set the stack pointer to R7
        self.reg[7] = 0xF4

    # Should accept the address to read and return the value
    def ram_read(self, address):
        return self.ram[address]

    # Should accept an address and value and store the value at that address
    def ram_write(self, address):
        self.ram[address] = self.value

    def LDI(self, i, v):
        self.reg[i] = v
        self.pc += 3

    def PRN(self, i, v):
        print(self.reg[i])
        self.pc += 2

    def HLT(self, i, v):
        self.running = False

    def MUL(self, reg_a, reg_b):
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3

    def ADD(self, reg_a, reg_b):
        self.alu('ADD', reg_a, reg_b)
    
    def PUSH(self, *args):
        self.reg[7] -= 1
        register_index = self.ram[self.pc + 1]
        self.ram[self.reg[7]] = self.reg[register_index]
        self.pc += 2

    def POP(self, i, v):
        register_index = self.ram[self.pc + 1]
        self.reg[register_index] = self.ram[self.reg[7]]
        self.reg[7] += 1
        self.pc += 2

    def CALL(self, *args):
        # Store next instruction in the stack
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.pc + 2
        # Move program counter to address stored in register
        register_index = self.ram[self.pc + 1]
        self.pc = self.reg[register_index]

    def RET(self, *args):
        # Pop from the stack
        address = self.ram[self.reg[7]]
        register_index = self.ram[self.pc + 1]
        self.reg[register_index] = self.ram[self.reg[7]]
        self.reg[7] += 1
        # Update program counter
        self.pc = address
        
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def load(self, fileName):
        """Load a program into memory"""
        address = 0
        with open(fileName) as file:
            for line in file:
                line = line.split('#')[0].strip()
                try:
                    instruction = int(line, 2)
                    self.ram[address] = instruction
                    address += 1
                except ValueError:
                    continue

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU"""
        try:
            while self.running:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                ir = self.ram[self.pc]
                if ir in self.branch_table:
                    self.branch_table[ir](reg_a, reg_b)
                else:
                    self.pc += 1
        except:
            raise Exception(f"Unknown instruction: {self.ram[self.pc]}")