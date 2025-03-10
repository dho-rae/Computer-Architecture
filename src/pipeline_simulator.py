import copy

# Masks:

# 111111 00000 00000 00000 00000 000000 = 0xFC000000
# 000000 11111 00000 00000 00000 000000 = 0x3E00000
# 000000 00000 11111 00000 00000 000000 = 0x1F0000
# 000000 00000 00000 11111 00000 000000 = 0xF800
# 000000 00000 00000 00000 11111 000000 = 0x7C0
# 000000 00000 00000 00000 00000 111111 = 0x3F
# 000000 00000 00000 11111 11111 111111 = 0xFFFF


def bits_0_to_15(Inst):
    return Inst & 0xFFFF


def bits_0_to_5(Inst):
    return Inst & 0x3F


def shifted_bits_6_to_10(Inst):
    return (Inst & 0x7C0) >> 6


def shifted_bits_11_to_15(Inst):
    return (Inst & 0xF800) >> 11


def shifted_bits_16_to_20(Inst):
    return (Inst & 0x1F0000) >> 16


def shifted_bits_21_to_25(Inst):
    return (Inst & 0x3E00000) >> 21


def shifted_bits_26_to_31(Inst):
    return (Inst & 0xFC000000) >> 26


def twos_complement(signed_value):
    if signed_value & (1 << 15):
        signed_value = signed_value - (1 << 16)
    return signed_value


class Reset:
    def reset(self):
        for attr, value in self.__dict__.items():
            setattr(self, attr, 0)


class IF_ID(Reset):

    def __init__(self, Inst, IncrPC):
        self.Inst = Inst
        self.IncrPC = IncrPC


class ID_EX(Reset):

    def __init__(self):
        self.Inst = 0x0
        self.RegDst = 0
        self.ALUSrc = 0
        self.ALUOp = 0
        self.MemRead = 0
        self.MemWrite = 0
        self.Branch = 0
        self.MemToReg = 0
        self.RegWrite = 0
        self.SEOffset = 0
        self.IncrPC = 0
        self.ReadReg1Value = 0
        self.ReadReg2Value = 0
        self.WriteReg1 = None
        self.WriteReg2 = None
        self.WriteReg_20_16 = 0
        self.WriteReg_15_11 = 0
        self.Func = 0x0
        self.Opcode = 0x0

    def instruction_decode(self, Inst, IncrPC):
        self.Inst = Inst
        self.IncrPC = IncrPC
        Opcode = shifted_bits_26_to_31(Inst)
        self.Opcode = Opcode

        if Opcode == 0:  # R-format
            Src1 = shifted_bits_21_to_25(Inst)
            Src2 = shifted_bits_16_to_20(Inst)
            Dest = shifted_bits_11_to_15(Inst)
            Func = bits_0_to_5(Inst)

            if Func == 0x0:  # nop
                pass

            elif Func == 0x20 or Func == 0x22:  # add/sub
                self.RegDst = 1
                self.ALUSrc = 0
                self.MemToReg = 0
                self.RegWrite = 1
                self.MemRead = 0
                self.MemWrite = 0
                self.Branch = 0
                self.ALUOp = 0b10

                if Func == 0x20:
                    self.Func = 0x20
                if Func == 0x22:
                    self.Func = 0x22

                self.WriteReg_20_16 = str(Src2)
                self.WriteReg_15_11 = str(Dest)
                self.ReadReg1Value = Regs[Src1]
                self.ReadReg2Value = Regs[Src2]
                self.SEOffset = 0

        else:  # I-format
            Src1 = shifted_bits_21_to_25(Inst)
            Dest = shifted_bits_16_to_20(Inst)
            Offset = bits_0_to_15(Inst)

            if Opcode == 0x20:  # lb
                self.RegDst = 0
                self.ALUSrc = 1
                self.MemToReg = 1
                self.RegWrite = 1
                self.MemRead = 1
                self.MemWrite = 0
                self.Branch = 0
                self.ALUOp = 0b00
                self.WriteReg_20_16 = str(Dest)
                self.WriteReg_15_11 = 0
                self.ReadReg1Value = Regs[Src1]
                self.ReadReg2Value = Regs[Dest]
                self.Func = None
                self.SEOffset = twos_complement(Offset)

            elif Opcode == 0x28:  # sb
                self.RegDst = None
                self.ALUSrc = 1
                self.MemToReg = None
                self.RegWrite = 0
                self.MemRead = 0
                self.MemWrite = 1
                self.Branch = 0
                self.ALUOp = 0b00
                self.Func = None
                self.WriteReg_20_16 = str(Dest)
                self.WriteReg_15_11 = 0
                self.ReadReg1Value = Regs[Src1]
                self.ReadReg2Value = Regs[Dest]


class EX_MEM(Reset):

    def __init__(self):
        self.Func = None
        self.WriteReg2 = None
        self.WriteReg1 = None
        self.MemRead = 0
        self.MemWrite = 0
        self.Branch = 0
        self.MemToReg = 0
        self.RegWrite = 0
        self.ReadReg1Value = 0
        self.ReadReg2Value = 0
        self.SEOffset = 0
        self.ALUOp = 0
        self.IncrPC = 0
        self.CalcBTA = None
        self.Zero = 0
        self.ALUResult = 0
        self.SWValue = 0
        self.WriteRegNum = 0

    def execute(self, MemRead, MemWrite, Branch, RegWrite, ALUOp, ReadReg1Value, ReadReg2Value, SEOffset,
                Func, IncrPC, opcode, RegDst, WriteReg_20_16, WriteReg_15_11, MemToReg):
        self.MemRead = MemRead
        self.MemWrite = MemWrite
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        self.Branch = Branch
        self.IncrPC = IncrPC
        self.CalcBTA = self.calculate_BTA()

        if RegDst == 1:  # r
            self.WriteRegNum = WriteReg_15_11
        elif RegDst == 0:  # load
            self.WriteRegNum = WriteReg_20_16
        else:  # stores
            self.WriteRegNum = None

        if ALUOp == 0b10:  # R-format
            if Func == 0x20:  # add
                self.ALUResult = ReadReg1Value + ReadReg2Value
                self.SWValue = ReadReg2Value
            elif Func == 0x22:  # sub
                self.ALUResult = ReadReg1Value - ReadReg2Value
                self.SWValue = ReadReg2Value
            elif Func == 0x0:  # nop
                pass

        if ALUOp == 0b00:  # I-format
            if opcode == 0x20:  # lb
                self.ALUResult = ReadReg1Value + SEOffset
                self.SWValue = ReadReg2Value
            elif opcode == 0x28:  # sb
                self.ALUResult = ReadReg1Value + SEOffset
                self.SWValue = ReadReg2Value

    @staticmethod
    def calculate_BTA():
        BTA = 'X'
        return BTA


class MEM_WB(Reset):

    def __init__(self):
        self.MemToReg = 0
        self.RegWrite = 0
        self.MemRead = 0
        self.MemWrite = 0
        self.Branch = 0
        self.RegWrite = 0
        self.LWDataValue = 0
        self.SWDataValue = 0
        self.ALUResult = 0
        self.WriteRegNum = 0

    def access_memory(self, MemToReg, RegWrite, ALUResult, WriteRegNum, MemRead, SWValue, MemWrite):
        self.MemToReg = MemToReg
        self.RegWrite = RegWrite
        self.ALUResult = ALUResult
        self.WriteRegNum = WriteRegNum
        self.SWDataValue = SWValue

        if MemRead == 1:  # load
            self.LWDataValue = Main_Mem[ALUResult]
        elif MemWrite == 1:  # store
            Main_Mem[ALUResult] = SWValue
        else:
            pass

    def write_back(self):
        global Regs

        if self.WriteRegNum is not None:
            if self.MemWrite == 0 and self.MemToReg == 0:  # r
                Regs[int(self.WriteRegNum)] = self.ALUResult

            elif self.MemWrite == 0 and self.MemToReg == 1:  # lb
                self.LWDataValue = Main_Mem[self.ALUResult]
                Regs[int(self.WriteRegNum)] = self.LWDataValue


def get_instruction_description(Opcode, Src1, Src2, Dest, Func):
    if Opcode == 0 and Func == 0:  # nop
        return "[ nop ]"
    elif Opcode == 0x20:  # lb
        return "[ lb $" + str(Dest) + ", " + str(Src1) + "(" + str(Src2) + ") ]"
    elif Opcode == 0x28:  # sb
        return "[ sb $" + str(Dest) + ", " + str(Src1) + "(" + str(Src2) + ") ]"
    elif Opcode == 0:  # R-format
        if Func == 0x20:  # add
            return "[ add $" + str(Dest) + ", $" + str(Src1) + ", $" + str(Src2) + " ]"
        elif Func == 0x22:  # sub
            return "[ sub $" + str(Dest) + ", $" + str(Src1) + ", $" + str(Src2) + " ]"
    else:
        return "[ Unknown Instruction ]"


def Print_out_everything(clock_cycle):
    cycle_label = f'\nClock Cycle {clock_cycle} (Before we copy the write side of pipeline registers to the read side)'
    print(cycle_label)

    print('\nRegisters:')
    for regNum, reg in enumerate(Regs):
        print('[ $' + str(regNum), '=', hex(reg), ']'),

    print('\nIF/ID_Write (written to by the IF stage)')
    if IF_ID_WRITE.Inst == 0:
        print('\tInst = 0x00000000')
    else:
        inst_hex = hex(IF_ID_WRITE.Inst)
        Opcode = shifted_bits_26_to_31(IF_ID_WRITE.Inst)
        Src1 = shifted_bits_21_to_25(IF_ID_WRITE.Inst)
        Src2 = shifted_bits_16_to_20(IF_ID_WRITE.Inst)
        Dest = shifted_bits_11_to_15(IF_ID_WRITE.Inst)
        Func = bits_0_to_5(IF_ID_WRITE.Inst)
        instruction_desc = get_instruction_description(Opcode, Src1, Src2, Dest, Func)
        IncrPC = IF_ID_WRITE.IncrPC
        print('\tInst =', inst_hex, '\t', instruction_desc, '\tIncrPC =', hex(IncrPC).lstrip('0x'))

    print('\nIF/ID_Read (read by the ID stage)')
    if IF_ID_READ.Inst == 0:
        print('\tInst = 0x00000000')
    else:
        inst_hex = hex(IF_ID_READ.Inst)
        Opcode = shifted_bits_26_to_31(IF_ID_READ.Inst)
        Src1 = shifted_bits_21_to_25(IF_ID_READ.Inst)
        Src2 = shifted_bits_16_to_20(IF_ID_READ.Inst)
        Dest = shifted_bits_11_to_15(IF_ID_READ.Inst)
        Func = bits_0_to_5(IF_ID_READ.Inst)
        instruction_desc = get_instruction_description(Opcode, Src1, Src2, Dest, Func)
        IncrPC = IF_ID_READ.IncrPC
        print('\tInst =', inst_hex, '\t', instruction_desc, '\tIncrPC =', hex(IncrPC).lstrip('0x'))

    print('\nID/EX Write (written to by the ID stage)')
    print('\tControl: RegDst =', ID_EX_WRITE.RegDst, ', ALUSrc =', ID_EX_WRITE.ALUSrc, ', ALUOp =',
          bin(ID_EX_WRITE.ALUOp), ', MemRead =', ID_EX_WRITE.MemRead, ', MemWrite =', ID_EX_WRITE.MemWrite,
          ', Branch =', ID_EX_WRITE.Branch, ', MemToReg =', ID_EX_WRITE.MemToReg, ', RegWrite =', ID_EX_WRITE.RegWrite)

    if ID_EX_WRITE.Inst == 0:
        print('\n\tIncrPC = 0')
    else:
        print('\n\tIncrPC=', hex(ID_EX_WRITE.IncrPC).lstrip('0x'))

    print('\tReadReg1Value =', hex(ID_EX_WRITE.ReadReg1Value))
    print('\tReadReg2Value =', hex(ID_EX_WRITE.ReadReg2Value))

    SEOffset_val = int(ID_EX_WRITE.SEOffset) if isinstance(ID_EX_WRITE.SEOffset, str) else ID_EX_WRITE.SEOffset
    print('\tSEOffset =', hex(((abs(SEOffset_val) ^ 0xffff) + 1) & int('ffff', 16)))

    print('\tWriteReg_20_16 =', ID_EX_WRITE.WriteReg_20_16)
    print('\tWriteReg_15_11 =', ID_EX_WRITE.WriteReg_15_11)
    print('\tFunction =', hex(ID_EX_WRITE.Func) if ID_EX_WRITE.Func is not None else 'None')

    print('\nID/EX Read (read to by the EX stage)')
    print('\tControl: RegDst =', ID_EX_READ.RegDst, ', ALUSrc =', ID_EX_READ.ALUSrc, ', ALUOp =',
          bin(ID_EX_READ.ALUOp), ', MemRead =', ID_EX_READ.MemRead, ', MemWrite =', ID_EX_READ.MemWrite,
          ', Branch =', ID_EX_READ.Branch, ', MemToReg =', ID_EX_READ.MemToReg, ', RegWrite =', ID_EX_READ.RegWrite)

    if ID_EX_READ.Inst == 0:
        print('\n\tIncrPC = 0')
    else:
        print('\n\tIncrPC=', hex(ID_EX_READ.IncrPC).lstrip('0x'))

    print('\tReadReg1Value =', hex(ID_EX_READ.ReadReg1Value))
    print('\tReadReg2Value =', hex(ID_EX_READ.ReadReg2Value))

    print('\tSEOffset =', hex(((abs(ID_EX_READ.SEOffset) ^ 0xffff) + 1) & 0xffff))
    print('\tWriteReg_20_16 =', ID_EX_READ.WriteReg_20_16)
    print('\tWriteReg_15_11 =', ID_EX_READ.WriteReg_15_11)
    print('\tFunction =', hex(ID_EX_READ.Func) if ID_EX_READ.Func is not None else 'None')

    print('\nEX/MEM Write (written to by the EX stage)')
    print('\tControl: MemRead =', EX_MEM_WRITE.MemRead, ', MemWrite =', EX_MEM_WRITE.MemWrite, ', Branch =',
          EX_MEM_WRITE.Branch, ', MemToReg =', EX_MEM_WRITE.MemToReg, ', RegWrite =', EX_MEM_WRITE.RegWrite)

    print('\n\tCalcBTA =', EX_MEM_WRITE.CalcBTA)
    print('\tZero =', EX_MEM_WRITE.Zero)
    print('\tALUResult =', hex(EX_MEM_WRITE.ALUResult))

    print('\tSWValue =', hex(EX_MEM_WRITE.SWValue))
    print('\tWriteRegNum =', EX_MEM_WRITE.WriteRegNum)

    print('\nEX/MEM READ (read to by the MEM stage)')
    print('\tControl: MemRead =', EX_MEM_READ.MemRead, ', MemWrite =', EX_MEM_READ.MemWrite, ', Branch =',
          EX_MEM_READ.Branch, ', MemToReg =', EX_MEM_READ.MemToReg, ', RegWrite =', EX_MEM_READ.RegWrite)

    print('\n\tCalcBTA =', EX_MEM_READ.CalcBTA)
    print('\tZero =', EX_MEM_READ.Zero)
    print('\tALUResult =', hex(EX_MEM_READ.ALUResult))

    print('\tSWValue =', hex(EX_MEM_READ.SWValue))
    print('\tWriteRegNum =', EX_MEM_READ.WriteRegNum)

    print('\nMEM/WB Write (written to by the MEM stage)')
    print('\tControl: MemToReg =', MEM_WB_WRITE.MemToReg, ', RegWrite =', MEM_WB_WRITE.RegWrite)

    print('\n\tLWDataValue =', hex(MEM_WB_WRITE.LWDataValue))
    print('\tALUResult =', hex(MEM_WB_WRITE.ALUResult))
    print('\tWriteRegNum =', MEM_WB_WRITE.WriteRegNum)

    print('\nMEM/WB Read (read by the WB stage)')
    print('\tControl: MemToReg =', MEM_WB_READ.MemToReg, ', RegWrite =', MEM_WB_READ.RegWrite)

    print('\n\tLWDataValue =', hex(MEM_WB_READ.LWDataValue))
    print('\tALUResult =', hex(MEM_WB_READ.ALUResult))
    print('\tWriteRegNum =', MEM_WB_READ.WriteRegNum)



def Copy_write_to_read():
    global IF_ID_READ
    global ID_EX_READ
    global EX_MEM_READ
    global MEM_WB_READ

    IF_ID_READ = copy.deepcopy(IF_ID_WRITE)
    ID_EX_READ = copy.deepcopy(ID_EX_WRITE)
    EX_MEM_READ = copy.deepcopy(EX_MEM_WRITE)
    MEM_WB_READ = copy.deepcopy(MEM_WB_WRITE)

    def reset_all():
        IF_ID_WRITE.reset()
        ID_EX_WRITE.reset()
        EX_MEM_WRITE.reset()
        MEM_WB_WRITE.reset()

    reset_all()


def IF_stage(Inst, current_address):
    IF_ID_WRITE.Inst = Inst
    IF_ID_WRITE.IncrPC = current_address


def ID_stage():
    ID_EX_WRITE.instruction_decode(IF_ID_READ.Inst, IF_ID_READ.IncrPC)


def EX_stage():
    EX_MEM_WRITE.execute(ID_EX_READ.MemRead, ID_EX_READ.MemWrite, ID_EX_READ.Branch, ID_EX_READ.RegWrite,
                         ID_EX_READ.ALUOp, ID_EX_READ.ReadReg1Value, ID_EX_READ.ReadReg2Value, ID_EX_READ.SEOffset,
                         ID_EX_READ.Func, ID_EX_READ.IncrPC, ID_EX_READ.Opcode, ID_EX_READ.RegDst,
                         ID_EX_READ.WriteReg_20_16, ID_EX_READ.WriteReg_15_11,
                         ID_EX_READ.MemToReg)


def MEM_stage():
    MEM_WB_WRITE.access_memory(EX_MEM_READ.MemToReg, EX_MEM_READ.RegWrite, EX_MEM_READ.ALUResult,
                               EX_MEM_READ.WriteRegNum, EX_MEM_READ.MemRead, EX_MEM_READ.SWValue,
                               EX_MEM_READ.MemWrite)


def WB_stage():
    MEM_WB_READ.write_back()


start_address = 0x7a000

IF_ID_WRITE = IF_ID(0x0, start_address)
IF_ID_READ = IF_ID(0x0, 0x0)

ID_EX_WRITE = ID_EX()
ID_EX_READ = ID_EX()

EX_MEM_WRITE = EX_MEM()
EX_MEM_READ = EX_MEM()

MEM_WB_WRITE = MEM_WB()
MEM_WB_READ = MEM_WB()

Main_Mem = []
Regs = [0] * 32


def main():
    count = 0

    for x in range(0x0, 0x7FF + 1):
        Main_Mem.append(count)

        count += 1

        if count > 0xFF:
            count = 0

    for x in range(0, 32):
        Regs[x] = 0x100 + x

    Insts = [0xA1020000,
             0x810AFFFC,
             0x00831820,
             0x01263820,
             0x01224820,
             0x81180000,
             0x81510010,
             0x00624022,
             0x00000000,
             0x00000000,
             0x00000000,
             0x00000000]

    Print_out_everything(0)

    current_address = start_address

    for clockCycle in range(0, 12):
        Copy_write_to_read()
        Inst = Insts[clockCycle]
        IF_stage(Inst, current_address)
        ID_stage()
        EX_stage()
        MEM_stage()
        WB_stage()
        Print_out_everything(clockCycle + 1)

        current_address += 4


if __name__ == '__main__':
    main()
