import func

status = 0
all_vars = {}
ints = []
floats = []
chars = []
bools = []
line_num = 0
with open("source.txt", "rt") as f:
	for line in f:
		line_num += 1
		if func.comment(line):
			continue
		if status == 0:
			if line == "START\n":
				status = 1
				continue
			if (func.var(line)):
				vars = {}
				line = line[3:].strip()
				while not func._as(line):
					line, var, val = func.next(line)
					vars[var] = val
				line = line[3:]
				for k in vars.keys():
					if k in all_vars:
						print("The variable", k, "has been previously declared")
				if line == "INT":
					for k, v in vars.items():
						try:
							if v == '':
								all_vars[k] = 0
							else:
								all_vars[k] = int(v)
							ints.append(k)
						except:
							print("Unable to parse",v,"as INT")
							exit()
				if line == "FLOAT":
					for k, v in vars.items():
						try:
							if v == '':
								all_vars[k] = 0
							else:
								all_vars[k] = float(v)
							ints.append(k)
						except:
							print("Unable to parse",v,"as FLOAT")
							exit()
				elif line == "CHAR":
					for k, v in vars.items():
						if v == '':
							all_vars[k] = ''
						else:
							if len(v[1:-1]) != 1 or not (v[0] == v[-1] == '\''):
								print("Unable to parse",v,"as CHAR")
								exit()
							all_vars[k] = v[1:-1]
						chars.append(k)
				elif line == "BOOL":
					for k, v in vars.items():
						if v == '':
							all_vars[k] = "FALSE"
						else:
							if v[1:-1] == "TRUE" or v[1:-1] == "FALSE":
								all_vars[k] = v[1:-1]
							else:
								print("Unable to parse",v,"as BOOL")
								exit()
						bools.append(k)

		elif status == 1:
			if func.indented(line):
				line = line[1:]
				if line[:6] == "OUTPUT":
					func.output(line[7:], all_vars)
				elif line[:5] == "INPUT":
					all_vars.update(func.inp(line[6:], all_vars, ints, floats, chars, bools))
				else:
					expr = line.split("=")
					chk = len(expr)-1
					while chk > 1:
						if expr[chk-1][-1:] == ">" or expr[chk-1][-1:] == "<" or len(expr[chk-1]) == 0:
							if len(expr[chk-1]) == 0:
								strcmb = expr[chk-2] + "==" + expr[chk]
								expr = expr[:chk-2] + [strcmb] + expr[chk+1:]
							else:
								strcmb = expr[chk-1] + expr[chk-1][-1:] == "<" + "=" + expr[chk]
								expr = expr[:chk-1] + [strcmb] + expr[chk+1:]
						chk-=1
					# try:
					res = func.check_valid(expr[len(expr)-1], all_vars, ints, floats, bools, chars)
					# except Exception as e:
						# print(e, "in line", line_num)
						# exit()
					i = 0
					while i < len(expr)-1:
						expr[i] = expr[i].strip()
						if expr[i] in all_vars:
							if expr[i] in bools:
								if (res == "TRUE" or res == "FALSE"):
									all_vars[expr[i]] = res
								else:
									print("Cannot parse",res,"to a BOOL")
									exit()
							elif expr[i] in chars:
								if len(res) == 1:
									all_vars[expr[i]] = res
								else:
									print("Cannot parse", res, "to a CHAR")
									exit()
							elif expr[i] in ints:
								try:
									all_vars[expr[i]] = int(res)
								except ValueError:
									print("Cannot parse", res, "to an INT")
									exit()
							elif expr[i] in floats:
								try:
									all_vars[expr[i]] = float(res)
								except ValueError:
									print("Cannot parse", res, "to an FLOAT")
									exit()
						else:
							print("ERR: Unknown variable", expr[i])
							exit()
						i += 1
			else:
				if line != "STOP":
					print("Expected indent at line", line_num)
					exit()