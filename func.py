def comment(line):
	return line.strip()[0] == '*'

def var(line):
	return line.strip()[0:3] == "VAR"

def _as(line):
	return line.strip()[0:2] == "AS"

def next(line):
	try:
		eq = line.index("=")
	except:
		eq = 999
	try:
		ind = line.index(",")
	except:
		ind = line.index(" ")
	if eq < ind:
		return line[ind+1:].strip(), line[:eq].strip(), line[eq+1:ind].strip()
	return line[ind+1:].strip(), line[:ind].strip(), ""

def indented(line):
	return line[0] == '\t'

def check_valid(line, all_vars, ints, floats, bools, chars):
	par = 0
	wo_par = ''
	terms = []
	status = 0 # 0 - waiting for term, 1 - waiting for operator 
	l_num = 0
	term = ''
	is_num = True
	while l_num < len(line):
		c = line[l_num]
		if c == " ":
			l_num += 1
			continue
		if c == '(':
			if status != 0:
				if term == "NOT":
					terms.append("NOT")
				else:
					raise Exception("Unexpected character", c)
			par+=1
			terms.append('(')
		elif c == ')':
			par-=1
			status = 1
			if par < 0:
				raise Exception("Invalid expression")
			if term == '':
				pass
			elif is_num:
				try:
					terms.append(float(term))
				except Exception as e:
					raise e
			else:
				term = term.strip()
				if term[0] == '\'' and term[-1] == '\'':
					terms.append(term[1:-1])
				elif term in all_vars:
					terms.append(all_vars[term])
				else:
					raise Exception("Unknown variable " + term)
				terms.append(all_vars[term])
			term = ''
			terms.append(')')
		else:
			op = is_operator(line, l_num)
			if op > 0 and not (op == 1 and line[l_num] == '-' and status == 0):
				status = 0
				term = term.strip()
				if is_num and term != '':
					try:
						terms.append(float(term))
					except ValueError as e:
						raise e
				elif term != '':
					term = term.strip()
					if term[0] == '\'' and term[-1] == '\'':
						terms.append(term[1:-1])
					elif term in all_vars:
						terms.append(all_vars[term])
					else:
						raise Exception("Unknown variable " + term)
				term = ''
				terms.append(line[l_num:l_num+op])
				l_num += op
				wo_par += c
				continue
			else:
				if status == 0:
					status = 1
					is_num = c == '-' or (c >= '0' and c <= '9')
				term += c
			wo_par += c
		l_num+=1
	if par != 0:
		raise Exception("Invalid expression")
	term = term.strip()
	if term.strip() != '':
		if is_num:
			try:
				terms.append(float(term))
			except Exception as e:
				raise e
		else:
			term = term.strip()
			if term[0] == '\'' and term[-1] == '\'':
				terms.append(term[1:-1])
			elif term in all_vars:
				terms.append(all_vars[term])
			else:
				raise Exception("Unknown variable " + term)
	return evaluate(terms)[0]

def is_operator(line, l_num):
	if line[l_num:l_num+3] == "AND" or line[l_num:l_num+3] == "NOT":
		return 3
	if line[l_num:l_num+2] == ">=" or line[l_num:l_num+2] == "<=" or line[l_num:l_num+2] == "==" or line[l_num:l_num+2] == "<>" or line[l_num:l_num+2] == "OR":
		return 2
	if line[l_num] == '+' or line[l_num] == '-' or line[l_num] == '*' or line[l_num] == '/' or line[l_num] == '%' or line[l_num] == '<' or line[l_num] == '>':
		return 1
	return 0

def evaluate(terms):
	while True:
		try:
			par_o = terms.index('(')
			row = par_o + 1
			par = 0
			while row < len(terms):
				if terms[row] == '(':
					par += 1
				elif terms[row] == ')':
					if par == 0:
						break
					else:
						par -= 1
				row += 1
			res = evaluate(terms[par_o+1:row])
			terms = terms[:par_o] + res + terms[row+1:]
		except ValueError:
			while len(terms) > 1:
				not_op = -1
				not_cnt = terms.count('NOT')
				if not_cnt > 0:
					not_op = terms.index('NOT')
					op_ind = not_op
					rhs = terms[op_ind+1]
					if rhs == 'TRUE':
						rhs = True
					elif rhs == 'FALSE':
						rhs = False
					ans = not rhs
					if ans == True:
						ans = 'TRUE'
					else:
						ans = 'FALSE'
					terms = terms[:op_ind] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				mul_op = div_op = mod_op = -1
				mul_cnt = terms.count('*')
				div_cnt = terms.count('/')
				mod_cnt = terms.count('%')
				if mul_cnt > 0:
					mul_op = terms.index('*')
				if div_cnt > 0:
					div_op = terms.index('/')
				if mod_cnt > 0:
					mod_op = terms.index('%')
				all_ops = [mul_op, div_op, mod_op]
				least = find_least(all_ops)
				if least != -1:
					op_ind = all_ops[least]
					lhs = terms[op_ind-1]
					rhs = terms[op_ind+1]
					if least == 0: # multiplication
						ans = lhs * rhs
					elif least == 1: # division
						ans = lhs / rhs
					elif least == 2: # modulo
						ans = lhs % rhs
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				add_op = sub_op = -1
				add_cnt = terms.count('+')
				sub_cnt = terms.count('-')
				if add_cnt > 0:
					add_op = terms.index('+')
				if sub_cnt > 0:
					sub_op = terms.index('-')
				all_ops = [add_op, sub_op]
				least = find_least(all_ops)
				if least != -1:
					op_ind = all_ops[least]
					lhs = terms[op_ind-1]
					rhs = terms[op_ind+1]
					if least == 0: # addition
						ans = lhs + rhs
					elif least == 1: # subtraction
						ans = lhs - rhs
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				gt_op = lt_op = gte_op = lte_op = -1
				gt_cnt = terms.count('>')
				lt_cnt = terms.count('<')
				gte_cnt = terms.count('>=')
				lte_cnt = terms.count('<=')
				if gt_cnt > 0:
					gt_op = terms.index('>')
				if lt_cnt > 0:
					lt_op = terms.index('<')
				if gte_cnt > 0:
					gte_op = terms.index('>=')
				if lte_cnt > 0:
					lte_op = terms.index('<=')
				all_ops = [gt_op, lt_op, gte_op, lte_op]
				least = find_least(all_ops)
				if least != -1:
					op_ind = all_ops[least]
					lhs = terms[op_ind-1]
					rhs = terms[op_ind+1]
					if least == 0: # greater than
						ans = lhs > rhs
					elif least == 1: # less than
						ans = lhs < rhs
					if least == 0: # greater than or equal to
						ans = lhs >= rhs
					elif least == 1: # less than or equal to
						ans = lhs <= rhs
					if ans == True:
						ans = 'TRUE'
					else:
						ans = 'FALSE'
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				eq_op = neq_op = -1
				eq_cnt = terms.count('==')
				neq_cnt = terms.count('<>')
				if eq_cnt > 0:
					eq_op = terms.index('==')
				if neq_cnt > 0:
					neq_op = terms.index('<>')
				all_ops = [eq_op, neq_op]
				least = find_least(all_ops)
				if least != -1:
					op_ind = all_ops[least]
					lhs = terms[op_ind-1]
					if lhs == 'TRUE':
						lhs = True
					elif lhs == 'FALSE':
						lhs = False
					rhs = terms[op_ind+1]
					if rhs == 'TRUE':
						rhs = True
					elif rhs == 'FALSE':
						rhs = False
					if least == 0: # equal to
						ans = lhs == rhs
					elif least == 1: # not equal to
						ans = lhs != rhs
					if ans == True:
						ans = 'TRUE'
					else:
						ans = 'FALSE'
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				and_op = -1
				and_cnt = terms.count('AND')
				if and_cnt > 0:
					and_op = terms.index('AND')
					op_ind = and_op
					lhs = terms[op_ind-1]
					if lhs == 'TRUE':
						lhs = True
					elif lhs == 'FALSE':
						lhs = False
					rhs = terms[op_ind+1]
					if rhs == 'TRUE':
						rhs = True
					elif rhs == 'FALSE':
						rhs = False
					ans = lhs and rhs
					if ans == True:
						ans = 'TRUE'
					else:
						ans = 'FALSE'
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			while len(terms) > 1:
				or_op = -1
				or_cnt = terms.count('OR')
				if or_cnt > 0:
					or_op = terms.index('OR')
					op_ind = or_op
					lhs = terms[op_ind-1]
					if lhs == 'TRUE':
						lhs = True
					elif lhs == 'FALSE':
						lhs = False
					rhs = terms[op_ind+1]
					if rhs == 'TRUE':
						rhs = True
					elif rhs == 'FALSE':
						rhs = False
					ans = lhs or rhs
					if ans == True:
						ans = 'TRUE'
					else:
						ans = 'FALSE'
					terms = terms[:op_ind-1] + [ans] + terms[op_ind+2:]
				else:
					break
			if len(terms) > 1:
				raise Exception("Invalid expression")
			return terms

def find_least(items):
	ind = -1
	low = -1
	_ind = 0
	while _ind < len(items):
		if items[_ind] != -1 and (low == -1 or items[_ind] < low):
			low = items[_ind]
			ind = _ind
		_ind += 1
	return ind

def output(line, all_vars):
	terms = line.split("&")
	for term in terms:
		term = term.strip()
		if term[0] == "\"" and term[-1] == "\"":
			i = 0
			term = term[1:-1]
			while i < len(term):
				c = term[i]
				if c == '[' and term[i+2] == ']':
					print(term[i+1], end="")
					i+=2
				elif c == '#':
					print()
				else:
					print(c, end="")
				i+=1
		else:
			if term in all_vars:
				print(all_vars[term], end="")
			else:
				raise Exception("Unknown variable", term)

def inp(line, all_vars, ints, floats, chars, bools):
	line = line.strip()
	terms = line.split(",")
	for term in terms:
		term = term.strip()
		if term not in all_vars:
			raise Exception("Undeclared variable:", term)
	user = input()
	items = user.split(",")
	if len(terms) != len(items):
		raise Exception("Expected input:", len(terms), ", received:", len(items))
	i = 0
	while i < len(terms):
		term = terms[i].strip()
		item = items[i].strip()
		if term in ints:
			all_vars[term] = int(item)
		elif term in floats:
			all_vars[term] = float(item)
		elif term in chars:
			if len(item[1:-1]) != 1 or not (item[0] == item[-1] == '\''):
				raise Exception("Unable to parse",item,"as CHAR")
			all_vars[term] = item[1:-1]
		elif term in bools:
			if item[1:-1] == "TRUE" or item[1:-1] == "FALSE":
				all_vars[term] = item[1:-1]
			else:
				raise Exception("Unable to parse",item,"as BOOL")
		i += 1
	return all_vars