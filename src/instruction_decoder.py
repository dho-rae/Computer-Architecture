# Masks:

# 111111 00000 00000 00000 00000 000000 = 0xFC000000
# 000000 11111 00000 00000 00000 000000 = 0x3E00000
# 000000 00000 11111 00000 00000 000000 = 0x1F0000
# 000000 00000 00000 11111 00000 000000 = 0xF800
# 000000 00000 00000 00000 11111 000000 = 0x7C0
# 000000 00000 00000 00000 00000 111111 = 0x3F
# 000000 00000 00000 11111 11111 111111 = 0xFFFF

def Bits_0_to_15(All_32_Bits):
    return All_32_Bits & 0xFFFF

def Bits_0_to_5(All_32_Bits):
    return All_32_Bits & 0x3F

def Shifted_Bits_6_to_10(All_32_Bits):
    return (All_32_Bits & 0x7C0) >> 6

def Shifted_Bits_11_to_15(All_32_Bits):
    return (All_32_Bits & 0xF800) >> 11

def Shifted_Bits_16_to_20(All_32_Bits):
    return (All_32_Bits & 0x1F0000) >> 16

def Shifted_Bits_21_to_25(All_32_Bits):
    return (All_32_Bits & 0x3E00000) >> 21

def Shifted_Bits_26_to_31(All_32_Bits):
    return (All_32_Bits & 0xFC000000) >> 26

# Function to carry out the two's complement conversion
def Twos_Complement(signed_value):
    if signed_value & (1 << 15):
        signed_value = signed_value - (1 << 16)
    return signed_value

All_32_Bit_Instructions = [0x032BA020, 0x8CE90014, 0x12A90003, 0x022DA822, 0xADB30020, 0x02697824, 0xAE8FFFF4, 0x018C6020, 0x02A4A825, 0x158FFFF7, 0x8ECDFFF0]

# Assume that the first instruction begins at address hex 9A040
Current_Address = 0x9A040

for All_32_Bits in All_32_Bit_Instructions:

    Opcode = Shifted_Bits_26_to_31(All_32_Bits)

    # R-format:
    if Opcode == 0:
        SrcReg1 = Shifted_Bits_21_to_25(All_32_Bits)
        SrcReg2 = Shifted_Bits_16_to_20(All_32_Bits)
        DestReg = Shifted_Bits_11_to_15(All_32_Bits)
      # X = Shifted_Bits_6_to_10(All_32_Bits)
        Func = Bits_0_to_5(All_32_Bits)

        if Func == 0x20:
            print(f"{hex(Current_Address)} add ${DestReg}, ${SrcReg1}, ${SrcReg2}")
        elif Func == 0x22:
            print(f"{hex(Current_Address)} sub ${DestReg}, ${SrcReg1}, ${SrcReg2}")
        elif Func == 0x24:
            print(f"{hex(Current_Address)} and ${DestReg}, ${SrcReg1}, ${SrcReg2}")
        elif Func == 0x25:
            print(f"{hex(Current_Address)} or ${DestReg}, ${SrcReg1}, ${SrcReg2}")
        elif Func == 0x2A:
            print(f"{hex(Current_Address)} slt ${DestReg}, ${SrcReg1}, ${SrcReg2}")

    else:
        # I-format:
        SrcReg = Shifted_Bits_21_to_25(All_32_Bits)
        DestReg = Shifted_Bits_16_to_20(All_32_Bits)
        Offset = Bits_0_to_15(All_32_Bits)

        if Opcode == 0x4:
            print(f"{hex(Current_Address)} beq ${DestReg}, ${SrcReg}, address {hex(Current_Address + 4 + (Twos_Complement(Offset) << 2))}")
        elif Opcode == 0x5:
            print(f"{hex(Current_Address)} bne ${DestReg}, ${SrcReg}, address {hex(Current_Address + 4 + (Twos_Complement(Offset) << 2))}")
        elif Opcode == 0x23:
            print(f"{hex(Current_Address)} lw ${DestReg}, {Twos_Complement(Offset)} (${SrcReg})")
        elif Opcode == 0x2B:
            print(f"{hex(Current_Address)} sw ${DestReg}, {Twos_Complement(Offset)} (${SrcReg})")

    # Update the address for the following instruction
    Current_Address += 4
