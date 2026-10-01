from string import *
f = open("commands.txt")
f1 = open("commanders.txt")
f2 = open("minus_cmds.txt")
f.readline()
table, potok, minus_cmds = [], [], []
alph = (ascii_uppercase + ascii_lowercase)
full_alph = ":0123456789ABCDEFabcdef"
for s in f:
    number, command, op1, op2, mask = s.split()
    table.append([command, mask, op1, op2])
for s1 in f1:
    potok.extend(s1.split())
for s2 in f2:
    minus_cmds.extend(s2.split())


def operands(finall_mask, actual_mask):
    R1, R2, Add, operand3 = "", "", "", ""
    for m in range(len(finall_mask)):
        if actual_mask[m] in ascii_lowercase and actual_mask[m] == "d":
            R1 += finall_mask[m]
        if actual_mask[m] in alph and actual_mask[m] == "r":
            R2 += finall_mask[m]
        if actual_mask[m] in alph and actual_mask[m] in "AaPpKkq":
            Add += finall_mask[m]
        if actual_mask[m] in alph and actual_mask[m] in "sb":
            operand3 += finall_mask[m]
    return R1, R2, Add, operand3


def Little_E(command):
    number = command[5]
    full_command = command[9:len(command)-2]
    cmds, oper = [], []
    if len(cmds) == 0:
        c1 = str(full_command[:4])
        c2 = c1[2:] + c1[:2]
        cmds.append(c2)
        oper.append(c1)
        for c in range(len(full_command)//4 - 1):
            c3 = str(full_command[4 + 4 * c: 8 + 4 * c])
            c4 = c3[2:] + c3[:2]
            cmds.append(c4)
            oper.append(c3)
    return cmds, number, oper


def program():
    AVR_command = str(input(""))
    if AVR_command.lower() == "exit":
        return False
    for ch in AVR_command:
        if ch not in full_alph:
            print("Команда введена неверно")
            return True
    s = AVR_command[1:]
    check_summ = int(s[:2], 16)
    for c_s in range(len(s) // 2 - 1):
        check_summ += int(s[2 + 2 * c_s: 4 + 2 * c_s], 16)
    if check_summ % 256 != 0:
        print("Неверная команда")
        return True
    if len(AVR_command) == 11:
        print("void")
        return True
    elif (len(AVR_command)-1) % 2 == 0:
        bit_counter = 0
        list_of_commands, skip_index = [], []
        Little_Endian, num, oper = Little_E(AVR_command) # список для 4 байтовых команд, чтобы пропускать 2ю часть команды
        for i in range(len(Little_Endian)):
            if i in skip_index:
                continue
            False_commands, maybe_cmds = [], []
            mask_forming = ""
            for k in range(len(Little_Endian[i])):
                mask_forming += bin(int(Little_Endian[i][k], 16))[2:].zfill(4)
            f_mask = mask_forming
            for j in range(len(table)):
                if str(table[j][1])[:4] == f_mask[:4]:
                    maybe_cmds.append(table[j])
            if len(maybe_cmds) == 0:
                print(f"Команда не найдена, номер строки {i}")
                continue
            for h in range(len(maybe_cmds)):
                cmd_mask = maybe_cmds[h][1]
                for p in range(4, len(f_mask)):
                    if cmd_mask[p] not in alph:
                        if str(cmd_mask)[p] != str(f_mask)[p]:
                            False_commands.append(maybe_cmds[h])
            for d in range(len(maybe_cmds)):
                if maybe_cmds[d] not in False_commands:
                    actual_mask = maybe_cmds[d][1]
                    # для команд, состоящих 2 команд, т.е 4 байт.
                    if len(actual_mask) == 32:
                        res = oper[i][:2] + " " + oper[i][2:] + " " + oper[i+1][:2] + " " + oper[i+1][2:]
                        skip_index.append(i+1)
                        second_command = Little_Endian[i+1]
                        s_c = ""
                        for l in range(len(second_command)):
                            s_c += bin(int(second_command[l], 16))[2:].zfill(4)
                        finall_mask = f_mask + s_c
                        R1, R2, Add, operand3 = operands(finall_mask, actual_mask)
                        b = hex(bit_counter).upper()[2:]
                        list_of_commands.append([f":{str(num)}{b}", res, maybe_cmds[d][0]])
                        if len(R1) != 0:
                            if maybe_cmds[d][2] == "r16":
                                list_of_commands[-1].append(f"r{16 + int(R1, 2)}")
                            else:
                                list_of_commands[-1].append(f"r{int(R1, 2)}")
                        if len(Add) != 0:
                            if maybe_cmds[d][0] in potok:
                                Add = hex(2 * int(Add, 2))[2:]
                                if maybe_cmds[d][0] == "jmp":
                                    if len(Add) > 1:
                                        list_of_commands[-1].append(f"0x{Add}")
                                    else:
                                        list_of_commands[-1].append(f"0x0{Add}")
                                else:
                                    if len(Add) > 1:
                                        list_of_commands[-1].append(f"0x{Add.upper()}")
                                    else:
                                        list_of_commands[-1].append(f"0x0{Add.upper()}")
                            else:
                                Add = hex(int(Add, 2))[2:]
                                if len(Add) > 1:
                                    list_of_commands[-1].append(f"0x{Add.upper()}")
                                else:
                                    list_of_commands[-1].append(f"0x0{Add.upper()}")
                        if len(R2) != 0:
                            if maybe_cmds[d][3] == "r16":
                                list_of_commands[-1].append(f"r{16 + int(R2, 2)}")
                            else:
                                list_of_commands[-1].append(f"r{int(R2, 2)}")
                        if len(operand3) != 0:
                            list_of_commands[-1].append(f"{int(operand3, 2)}")
                        bit_counter += 4
                        break # для того, чтобы остановился на первой найденной приоритеной команде
                    # для команд состоящих из одной команды, т.е 2 байт
                    else:
                        res = oper[i][:2] + " " + oper[i][2:]
                        R1, R2, Add, operand3 = operands(f_mask, actual_mask)
                        b = hex(bit_counter).upper()[2:]
                        list_of_commands.append([f":{str(num)}{b}", res, maybe_cmds[d][0]])
                        if len(R1) != 0:
                            if maybe_cmds[d][0] == "adiw" or maybe_cmds[d][0] == "sbiw":
                                list_of_commands[-1].append(f"r{24 + 2 * int(R1, 2)}") # умножаем на 2, чтобы всегда было чётное число
                            elif maybe_cmds[d][2] == "r16":
                                list_of_commands[-1].append(f"r{16 + int(R1, 2)}")
                            else:
                                list_of_commands[-1].append(f"r{int(R1, 2)}")
                        if len(Add) != 0:
                            if maybe_cmds[d][0] in potok:
                                Add = hex(2 * int(Add, 2))[2:]
                                if maybe_cmds[d][0] == "rjmp":
                                    k = int(Add, 16) // 2
                                    if k >= 2048:
                                        k -= 4096
                                    PC = int(num, 16) * 16 + bit_counter + 2 # первую цифру нужно умножать на 16, т.к работа ведётся в 16сс (для получения десятков)
                                    target = hex(PC + 2 * k)[2:]
                                    list_of_commands[-1].append(f"0x{target.upper()}")
                                elif maybe_cmds[d][0] == "rcall":
                                    k = int(Add, 16) // 2
                                    if k >= 2048: # K хранится в доп коде, поэтому для перевода в обычное отрицательное вычитаем 4096
                                        k -= 4096
                                    PC = int(num,16) * 16 + bit_counter + 2
                                    target = hex(PC + 2 * k)[2:]
                                    list_of_commands[-1].append(f"0x{target.upper()}")
                                elif maybe_cmds[d][0] in minus_cmds:
                                    k = int(Add, 16) // 2
                                    if k >= 64:
                                        k -= 128
                                    PC = int(num, 16) * 16 + bit_counter + 2
                                    target = hex(PC + 2 * k)[2:]
                                    list_of_commands[-1].append(f"0x{target.upper()}")
                                else:
                                    if len(Add) > 1:
                                        list_of_commands[-1].append(f"0x{Add.upper()}")
                                    else:
                                        list_of_commands[-1].append(f"0x0{Add.upper()}")
                            else:
                                Add = hex(int(Add, 2))[2:]
                                if maybe_cmds[d][0][:3] == "ldd" or maybe_cmds[d][0][:3] == "std":
                                    if maybe_cmds[d][0][-1] == "Y":
                                        if len(Add) > 1:
                                            list_of_commands[-1].append(f"Y+0x{Add.upper()}")
                                        else:
                                            list_of_commands[-1].append(f"Y+0x0{Add.upper()}")
                                    else:
                                        if len(Add) > 1:
                                            list_of_commands[-1].append(f"Z+0x{Add.upper()}")
                                        else:
                                            list_of_commands[-1].append(f"Z+0x0{Add.upper()}")
                                else:
                                    if len(Add) > 1:
                                        list_of_commands[-1].append(f"0x{Add.upper()}")
                                    else:
                                        list_of_commands[-1].append(f"0x0{Add.upper()}")
                        if len(R2) != 0:
                            if maybe_cmds[d][3] == "r16":
                                list_of_commands[-1].append(f"r{16 + int(R2, 2)}")
                            else:
                                list_of_commands[-1].append(f"r{int(R2, 2)}")
                        if len(operand3) != 0:
                            list_of_commands[-1].append(f"{int(operand3, 2)}")
                        bit_counter += 2
                        break # для того, чтобы остановился на первой найденной приоритеной команде
                elif len(maybe_cmds) == len(False_commands):
                    print(f"команда не найдена, номер команды = {i}")
            if len(list_of_commands[-1]) > 4:
                print(*list_of_commands[-1][:3], f"{list_of_commands[-1][3]}, {list_of_commands[-1][4]}")
            else:
                print(*list_of_commands[-1])
    else:
        print("команда AVR введена неверно")
    return True


print("Введите avr команду, чтобы получить asm код, либо exit для выхода из программы")
while True:
    if program() == False:
        print("Процесс закончен :)")
        break