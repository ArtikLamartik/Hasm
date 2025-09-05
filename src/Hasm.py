def compare_values(value1, value2, operator):
    def is_hex(val):
        try:
            int(val, 16)
            return True
        except ValueError:
            return False
    def convert_value(val):
        if isinstance(val, (int, float)):
            return val
        if is_hex(val):
            return int(val, 16)
        if isinstance(val, str):
            return val
        try:
            return float(val) if '.' in val else int(val)
        except ValueError:
            raise ValueError(f"Invalid value: {val}")
    value1 = convert_value(value1)
    value2 = convert_value(value2)
    if operator == "==":
        return value1 == value2
    elif operator == "!=":
        return value1 != value2
    elif operator == ">>":
        return value1 > value2
    elif operator == "<<":
        return value1 < value2
    elif operator == ">=":
        return value1 >= value2
    elif operator == "<=":
        return value1 <= value2
    else:
        raise ValueError("Invalid comparison operator")
Terminated = False
atexits = 0
atexit = 0
Registers = {
    "RA": 0,
    "RB": 0,
    "RC": 0,
    "RD": 0,
    "RE": 0,
    "RF": 0,
}
Logic = {
    "CMP": False,
    "ADC26": 0,
    "ADC27": 0,
    "ADC28": 0,
    "Pin": 0,
}
Stack = {}
CallStack = []
def run(filename):
    global Terminated, atexits, atexit, Registers, Logic, Stack, CallStack
    while True:
        try:
            from machine import ADC, Pin, PWM
            from time import sleep
            import sys
            with open(filename, 'r') as f:
                code = f.readlines()
                ln = 0
                label_map = {}
                new_code = []
                i = 0
                while i < len(code):
                    line = code[i].strip()
                    if line.startswith("label "):
                        label_name = line.split()[1]
                        label_map[label_name] = len(new_code)
                        i += 1
                        while i < len(code) and (code[i].strip() == "" or code[i][0].isspace()):
                            new_code.append(code[i].lstrip())
                            i += 1
                    else:
                        new_code.append(line)
                        i += 1
                code = new_code
                for lne in code:
                    if lne.startswith("atexit"):
                        atexits += 1
                while ln < len(code):
                    if Terminated:
                        break
                    line = code[ln].strip()
                    if not line or line.startswith(';'):
                        ln += 1
                        continue
                    elif line.startswith("halt"):
                        Terminated = True
                        sys.exit(0)
                    elif line.startswith("test"):
                        print("TEST", Registers, Logic, Stack, "TEST")
                    elif line.startswith("log"):
                        log_parts = line[3:].strip().split()
                        out = []
                        for part in log_parts:
                            if part in Registers:
                                out.append(str(Registers[part]))
                            elif part.startswith("@"):
                                addr = part[1:]
                                out.append(str(Stack.get(addr, 0)))
                            elif part in Logic:
                                out.append(str(Logic[part]))
                            else:
                                out.append(part)
                        print("[LOG]", ' '.join(out))
                    elif line.startswith("mov"):
                        parts = line.replace(',', '').split()
                        dest = parts[1]
                        src = parts[2]
                        value = None
                        if src in Registers:
                            value = Registers[src]
                        elif src.startswith("@"):
                            addr = src[1:]
                            if addr in Stack:
                                value = Stack[addr]
                            else:
                                value = 0
                        elif src in Logic and src != "CMP":
                            value = Logic[src]
                        elif src.startswith('"') or src.startswith("'") or src.startswith("`"):
                            quote_char = None
                            start = end = -1
                            for i, c in enumerate(line):
                                if quote_char is None and (c == '"' or c == "'" or c == "`"):
                                    quote_char = c
                                    start = i + 1
                                elif quote_char and c == quote_char:
                                    end = i
                                    break
                            if start != -1 and end != -1:
                                value = line[start:end]
                            else:
                                value = src
                        else:
                            try:
                                value = src
                            except ValueError as e:
                                print(e)
                                sys.exit(1)
                        if dest in Registers:
                            Registers[dest] = value
                        elif dest.startswith("@"):
                            addr = dest[1:]
                            Stack[addr] = value
                        elif dest in Logic and dest != "CMP":
                            Logic[dest] = value
                    elif line.startswith("ret"):
                        if CallStack:
                            ln = CallStack.pop() + 1
                            continue
                        else:
                            Terminated = True
                    elif line.startswith("add"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) + float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) + float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) + float(value2))
                        except:
                            pass
                    elif line.startswith("sub"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.replace(',', '').split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) - float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) - float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) - float(value2))
                        except:
                            pass
                    elif line.startswith("mul"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.replace(',', '').split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) * float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) * float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) * float(value2))
                        except:
                            pass
                    elif line.startswith("div"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.replace(',', '').split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) / float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) / float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) / float(value2))
                        except:
                            pass
                    elif line.startswith("idiv"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.replace(',', '').split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) // float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) // float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) // float(value2))
                        except:
                            pass
                    elif line.startswith("pow"):
                        try:
                            value1 = float(Registers[str(line.replace(',', '').split()[2])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[2]
                                int_address = address[1:]
                                value1 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value1 = float(Logic[line.replace(',', '').split()[2]])
                                except KeyError:
                                    value1 = float(line.replace(',', '').split()[2])
                        try:
                            value2 = float(Registers[str(line.replace(',', '').split()[3])])
                        except KeyError:
                            try:
                                address = line.replace(',', '').split()[3]
                                int_address = address[1:]
                                value2 = float(Stack[int_address])
                            except KeyError:
                                try:
                                    value2 = float(Logic[line.replace(',', '').split()[3]])
                                except KeyError:
                                    value2 = float(line.replace(',', '').split()[3])
                        try:
                            variable = line.replace(',', '').split()[1]
                            if variable.startswith("@"):
                                int_address = variable[1:]
                                Stack[int_address] = float(float(value1) ^ float(value2))
                            elif variable in Registers:
                                Registers[str(variable)] = float(float(value1) ^ float(value2))
                            elif variable in Logic and variable != "CMP":
                                Logic[str(variable)] = float(float(value1) ^ float(value2))
                        except:
                            pass
                    elif line.startswith("relcmp"):
                        Logic["CMP"] = False
                    elif line.startswith("jmpc"):
                        if Logic["CMP"] == True:
                            jump_value = line.split()[1]
                            if jump_value in label_map:
                                CallStack.append(ln)
                                ln = label_map[jump_value]
                            elif jump_value.startswith("+"):
                                jump_target = int(jump_value[1:])
                                ln += jump_target
                            elif jump_value.startswith("-"):
                                jump_target = -int(jump_value[1:])
                                ln += jump_target
                            else:
                                try:
                                    ln = int(jump_value) - 1
                                except:
                                    sys.exit(0)
                            if 0 <= ln < len(code):
                                continue
                            else:
                                sys.exit(0)
                    elif line.startswith("jmpnc"):
                        if Logic["CMP"] == False:
                            jump_value = line.split()[1]
                            if jump_value in label_map:
                                CallStack.append(ln)
                                ln = label_map[jump_value]
                            elif jump_value.startswith("+"):
                                jump_target = int(jump_value[1:])
                                ln += jump_target
                            elif jump_value.startswith("-"):
                                jump_target = -int(jump_value[1:])
                                ln += jump_target
                            else:
                                try:
                                    ln = int(jump_value) - 1
                                except:
                                    sys.exit(0)
                            if 0 <= ln < len(code):
                                continue
                            else:
                                sys.exit(0)
                    elif line.startswith("jmp"):
                        jump_value = line.split()[1]
                        if jump_value in label_map:
                            CallStack.append(ln)
                            ln = label_map[jump_value]
                        elif jump_value.startswith("+"):
                            jump_target = int(jump_value[1:])
                            ln += jump_target
                        elif jump_value.startswith("-"):
                            jump_target = -int(jump_value[1:])
                            ln += jump_target
                        else:
                            try:
                                ln = int(jump_value) - 1
                            except:
                                sys.exit(0)
                        if 0 <= ln < len(code):
                            continue
                        else:
                            sys.exit(0)
                    elif line.startswith("cmp"):
                        try:
                            value1 = str(Registers[str(line.split()[1])])
                        except KeyError:
                            try:
                                address = line.split()[1]
                                int_address = address[1:]
                                value1 = str(Stack[int_address])
                            except KeyError:
                                if line.split()[1] in ["ADC26", "ADC27", "ADC28", "Pin"]:
                                    value1 = str(float(Logic[str(line.split()[1])]))
                                else:
                                    value1 = str(float(line.split()[1]))
                        operator = str(line.split()[2])
                        try:
                            value2 = str(Registers[str(line.split()[3])])
                        except KeyError:
                            try:
                                address = line.split()[3]
                                int_address = address[1:]
                                value2 = str(Stack[int_address])
                            except KeyError:
                                if line.split()[3] in ["ADC26", "ADC27", "ADC28", "Pin"]:
                                    value2 = str(float(Logic[str(line.split()[3])]))
                                else:
                                    value2 = str(float(line.split()[3]))
                        Logic["CMP"] = compare_values(eval(value1), eval(value2), operator)
                    elif line.startswith("atexit"):
                        if atexit == 1:
                            jump_value = line.split()[1]
                            if jump_value in label_map:
                                CallStack.append(ln)
                                ln = label_map[jump_value]
                            elif jump_value.startswith("+"):
                                jump_target = int(jump_value[1:])
                                ln += jump_target
                            elif jump_value.startswith("-"):
                                jump_target = -int(jump_value[1:])
                                ln += jump_target
                            else:
                                try:
                                    ln = int(jump_value) - 1
                                except:
                                    sys.exit(0)
                            if 0 <= ln < len(code):
                                continue
                            else:
                                sys.exit(0)
                    elif line.startswith("//"):
                        pass
                    elif line.startswith("syscall"):
                        if int(Registers["RA"]) == 1:
                            Terminated = True
                            sys.exit(0)
                        elif int(Registers["RA"]) == 2:
                            sleep(float(Registers["RB"]))
                        elif int(Registers["RA"]) == 3:
                            if int(Registers["RC"]) == 0:
                                Pin(int(Registers["RB"]), Pin.OUT).value(int(Registers["RD"]))
                            elif int(Registers["RC"]) == 1:
                                Pin(int(Registers["RB"]), Pin.OUT).toggle()
                        elif int(Registers["RA"]) == 4:
                            if int(Registers["RC"]) == 1:
                                Logic["Pin"] = Pin(int(Registers["RB"]), Pin.IN, Pin.PULL_DOWN).value()
                            elif int(Registers["RC"]) == 0:
                                Logic["Pin"] = Pin(int(Registers["RB"]), Pin.IN, Pin.PULL_UP).value() ^ 1
                        elif int(Registers["RA"]) == 5:
                            Logic["ADC" + f"{int(Registers['RB'])}"] = ADC(Pin(int(Registers["RB"]))).read_u16()
                        elif int(Registers["RA"]) == 6:
                            pwm_pin = PWM(Pin(int(Registers["RB"])))
                            pwm_pin.freq(int(Registers["RC"]))
                            if Registers["RD"] == 0:
                                if 0 <= Registers["RE"] <= 65536:
                                    pwm_pin.duty_u16(int(Registers["RE"]))
                                elif 0 >= Registers["RE"]:
                                    pwm_pin.duty_u16(0)
                                elif 100 <= Registers["RE"]:
                                    pwm_pin.duty_u16(65535)
                            elif Registers["RD"] == 1:
                                if 0 <= Registers["RE"] <= 100:
                                    duty_value = int((Registers["RE"] / 100) * 65535)
                                    pwm_pin.duty_u16(duty_value)
                                elif 0 >= Registers["RE"]:
                                    pwm_pin.duty_u16(0)
                                elif 100 <= Registers["RD"]:
                                    pwm_pin.duty_u16(65535)
                        elif int(Registers["RA"]) == 7:
                            pass #for networking
                        elif int(Registers["RA"]) == 8:
                            log_parts = Registers["RB"].strip().split()
                            out = []
                            for part in log_parts:
                                if part in Registers:
                                    out.append(str(Registers[part]))
                                elif part.startswith("@"):
                                    addr = part[1:]
                                    out.append(str(Stack.get(addr, 0)))
                                elif part in Logic and part != "CMP":
                                    out.append(str(Logic[part]))
                                else:
                                    out.append(part)
                            print(' '.join(out))
                        elif int(Registers["RA"]) == 9:
                            dest = Registers["RC"]
                            user_input = input(Registers["RB"])
                            if dest.startswith("@"):
                                addr = dest[1:]
                                Stack[addr] = user_input
                            elif dest in Registers:
                                Registers[dest] = user_input
                            elif dest in Logic and dest != "CMP":
                                Logic[dest] = user_input
                    ln += 1
        except KeyboardInterrupt:
            atexit = 1
            if atexits == 0:
                sys.exit(0)
        except Exception as E:
            from machine import Pin
            Pin(22, Pin.OUT).value(1)
            print(E)
            if Pin(21, Pin.IN, Pin.PULL_UP).value() ^ 1 == 1:
                Terminated = False
                continue
            Terminated = True
