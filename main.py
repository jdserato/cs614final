import func

status = 0
all_vars = {}
reserved = {'IF', 'WHILE', 'OUTPUT', 'INPUT', 'START', 'STOP', 'VAR', 'AS', 'CHAR', 'INT', 'BOOL', 'FLOAT', 'ELSE', 'SWITCH', 'CASE', 'DEFAULT'}
ints = []
floats = []
chars = []
bools = []
lines = []
line_num = 0
find_stop = False
find_stat = 0
statements = []
prevstops = []
backline = []
sw_res = []
sw_ind = []
with open("testcases/source3.txt", "rt") as f:
	for line in f:
		lines.append(line)
	while line_num < len(lines):
		line = lines[line_num]
		line_num += 1
		if len(line.strip()) == 0 or func.comment(line):
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
						exit()
					if k in reserved or not ((k[0] >= 'a' and k[0] <= 'z') or (k[0] >= 'A' and k[0] <= 'Z') or k[0] == '_'):
						print("Invalid variable declaration:", k)
						exit()  
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
							floats.append(k)
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

		else:
			if func.stop(line) and status == 0:
				exit()
			if func.indented(line, status):
				line = line[status:]
				# print("line", line, "status", status)
				if line[:5] == "START":
					status += 1
					continue
				if find_stop:
					continue
				if len(statements) > 0 and statements[len(statements)-1] == "SWITCH" and sw_ind[len(sw_ind)-1] == status:
					if line[:4] == "CASE" or line[:7] == "DEFAULT":
						status += 1
						if line[:4] == "CASE":
							statements.append("CASE")
							res = func.check_valid(line[5:], all_vars, ints, floats, bools, chars)
							if res == sw_res[len(sw_res)-1]:
								# print("it is true")
								prevstops.append(False)
							else:
								# find stop
								find_stop = True
								prevstops.append(True)
								find_stat = status
						else:
							statements.append("DEFAULT")
							find_stop = False
						continue
					else:
						print("Expected CASE statement")
						exit()
				if line[:6] == "OUTPUT":
					func.output(line[7:], all_vars, ints, floats, chars, bools)
				elif line[:5] == "INPUT":
					all_vars.update(func.inp(line[6:], all_vars, ints, floats, chars, bools))
				elif line[:2] == "IF": # if statement.
					statements.append("IF")
					status += 1
					res = func.check_valid(line[3:], all_vars, ints, floats, bools, chars)
					if res == 'TRUE':
						# print("it is true")
						prevstops.append(False)
					elif res == "FALSE":
						# find stop
						find_stop = True
						prevstops.append(True)
						find_stat = status
					else:
						print("Invalid BOOL expression")
						exit()
				elif line[:4] == "ELSE": # else statement, should not run
					print(statements, "has been authorized for some reason")
					if len(statements) > 0 and statements[len(statements)-1] == "IF":
						statements.pop()
						if lines[line_num][status:][:4] == "ELSE":
							status += 1
							line_num += 1
							find_stop = not prevstops.pop()
					else:
						print("Unexpected ELSE statement")
						exit()
				elif line[:5] == "WHILE": 
					# print("While detected")
					statements.append("WHILE")
					backline.append(line_num)
					# print(backline)
					status += 1
					res = func.check_valid(line[6:], all_vars, ints, floats, bools, chars)
					if res == 'TRUE':
						# print("it is true")
						prevstops.append(False)
					elif res == "FALSE":
						# find stop
						find_stop = True
						prevstops.append(True)
				elif line[:6] == "SWITCH":
					# print(line, "line")
					statements.append("SWITCH")
					# backline.append(line_num)
					status += 1
					res = func.check_valid(line[7:], all_vars, ints, floats, bools, chars)
					sw_res.append(res)
					sw_ind.append(status+1)
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
					# print("expr", expr[len(expr)-1])
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
				if line[status-1:][:4] != "STOP":
					print("Expected indent at line", line_num, "errcode:", status)
					exit()
				else:
					# print("stop detected in status", status, "line", line_num)
					if find_stop and find_stat == status-1:
						find_stop = False
					status -= 2
					# print("new status", status)
					# print("status", status, "line", lines[line_num-1], "at line", line_num)
					if len(statements) > 0 :
						# print(statements)
						state = statements.pop()
						if state == "IF":
							# print("then", statements)
							if lines[line_num][status:][:4] == "ELSE":
								# print("EXECUTE")
								statements.append("ELSE")
								status += 1
								line_num += 1
								find_stop = not prevstops.pop()
						elif state == "WHILE":
							prevline = backline.pop()
							if prevstops.pop() == False:
								line_num = prevline - 1
								# print("GOTO", line_num, "stat", status)
							find_stop = False
						elif state == "SWITCH":
							sw_ind.pop()
							sw_res.pop()
							find_stop = False
						elif state == "CASE":
							if prevstops.pop() == False:
								find_stop = True
							else:
								find_stop == False
						elif state == "DEFAULT":
							find_stop = True