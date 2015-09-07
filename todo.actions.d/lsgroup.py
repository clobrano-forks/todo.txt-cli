import sys, os, re, subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

HIGHLIGHTS = (('(A)', bcolors.WARNING),
			  ('(B)', bcolors.OKGREEN),
			  ('(C)', bcolors.OKBLUE),
			  ('(D)', bcolors.HEADER))
COLUMN_W = 40
TERM_W = int(os.popen('stty size', 'r').read().split()[1])
TODOSH_DIR = os.getcwd()


def main(argv):
	contexts = []
	context_lines = []

	if len(argv) < 2:
		print 'ERROR'
		exit()
	# contexts or projects
	pre = '\+' if '-p' in argv else '@'


		# this ignores final filter and stuff
	"""
	with open(argv[0], "r") as f:
		lines = f.readlines()
		# append to end here and switch to front after sorting
		for i in range(len(lines)):
			lines[i] = lines[i].replace('\n', '') + ' ' + ('%02d' % (i + 1))
	"""

	# filter for only the actual lines
	# get no colors because strings are weird
	lines = [l for l in subprocess.check_output(['./todo.sh', '-p', 'ls'], cwd=TODOSH_DIR).split('\n') 
			if len(re.findall('^\d+', l)) > 0]
	
	# numbers from start to end so you can sort later on
	for i in range(len(lines)):
		num = re.findall('^\d+', lines[i])[0]
		lines[i] = re.sub('^\d+', '', lines[i])
		lines[i] = lines[i] + ' ' + num


	# rool through list and add projects into array if they're not there
	for l in lines:
		for r in re.findall('(' + pre + '[A-Za-z0-9]*)', l):
			if r not in contexts:
				contexts.append(r)
				context_lines.append([])
			context_lines[contexts.index(r)].append(l.strip())
	
	context_lengths = sorted([len(c) for c in context_lines])
	
	# balance the context list if context is 2x as big as next one
	if context_lengths[-1] * 2 > context_lengths[-2]:
		# find the index of biggest
		# you don't need next here because you know that you're gonna get something
		biggest = [i for i in range(len(context_lines)) 
				if len(context_lines[i]) == context_lengths[-1]][0]

		chunk1 = context_lines[biggest][:int(context_lengths[-1] / 2)]
		chunk2 = context_lines[biggest][int(context_lengths[-1] / 2):]

		context_lines[biggest] = chunk1
		context_lines.insert(biggest, chunk2)

		# copy biggest over one
		contexts.insert(biggest, contexts[biggest])
		print 'split %s into 2 sections.' % contexts[biggest]

	try:
		# sort lines
		for i in range(len(context_lines)):
			context_lines[i] = sorted(context_lines[i])

		# move number from end
		for i in range(len(context_lines)):
			for j in range(len(context_lines[i])):
				context_lines[i][j] = context_lines[i][j].split()[-1] \
				+ ' ' + ' '.join(context_lines[i][j].split()[:-1])

		# columns that will fit
		column_offset = 0
		columns = TERM_W / COLUMN_W
		while column_offset + columns < len(context_lines) + columns:
			# titles
			for i in range(column_offset, min(column_offset + columns, len(context_lines))):
				print contexts[i][:COLUMN_W].ljust(COLUMN_W),
			print ''

			count = 0
			empty = False;
			while not empty:
				# all the rows in this section
				empty = True;
				for i in range(column_offset, min(column_offset + columns, len(context_lines))):
					text = ''
					if count < len(context_lines[i]):
						empty = False
						text = context_lines[i][count]
						text = text.replace(contexts[i] + ' ', '')
					
					text = text[:COLUMN_W]
					text = text.ljust(COLUMN_W)
					
					for h in HIGHLIGHTS:
						text = text.replace(h[0], h[0] + h[1])
					print text + bcolors.ENDC,

				count += 1
				print ''

			column_offset += columns
	except:
		print 'ERROR'
		exit()


if __name__ == "__main__":
    main(sys.argv[1:])
