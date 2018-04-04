import os
import sys
import re
import chardet #@UnresolvedImport

class smiItem(object):
	def __init__(self):
		self.start_ms = 0L
		self.start_ts = '00:00:00,000'
		self.end_ms = 0L
		self.end_ts = '00:00:00,000'
		self.contents = None
		self.linecount = 0
		self.is_end = False
	@staticmethod
	def ms2ts(ms):
		hours = ms / 3600000L
		ms -= hours * 3600000L
		minutes = ms / 60000L
		ms -= minutes * 60000L
		seconds = ms / 1000L
		ms -= seconds * 1000L
		s = '%02d:%02d:%02d,%03d' % (hours, minutes, seconds, ms)
		return s
	def convertSrt(self):
		if self.linecount == 4:
			i=1 #@UnusedVariable
		# 1) convert timestamp
		self.start_ts = smiItem.ms2ts(self.start_ms)
		self.end_ts = smiItem.ms2ts(self.end_ms-10)
		# 2) remove new-line
		self.contents = re.sub(r'\s+', ' ', self.contents)
		# 3) remove web string like "&nbsp";
		self.contents = re.sub(r'&[a-z]{2,5};', '', self.contents)
		# 4) replace "<br>" with '\n';
		self.contents = re.sub(r'(<br>)+', '\n', self.contents, flags=re.IGNORECASE)
		# 5) find all tags
		fndx = self.contents.find('<')
		if fndx >= 0:
			contents = self.contents
			sb = self.contents[0:fndx]
			contents = contents[fndx:]
			while True:
				m = re.match(r'</?([a-z]+)[^>]*>([^<>]*)', contents, flags=re.IGNORECASE)
				if m == None: break
				contents = contents[m.end(2):]
				#if m.group(1).lower() in ['font', 'b', 'i', 'u']:
				if m.group(1).lower() in ['b', 'i', 'u']:
					sb += m.string[0:m.start(2)]
				sb += m.group(2)
			self.contents = sb
		self.contents = self.contents.strip()
		self.contents = self.contents.strip('\n')
	def __repr__(self):
		s = '%d:%d:<%s>:%d' % (self.start_ms, self.end_ms, self.contents, self.linecount)
		return s

###################################################################################################
def convertSMI(smi_file):
	if not os.path.exists(smi_file):
		sys.stderr.write('Cannot find smi file <%s>\n' % smi_file)
		return False
	rndx = smi_file.rfind('.')
	srt_file = '%s.srt' % smi_file[0:rndx]
	ifp = open(smi_file)
	smi_sgml = ifp.read()#.upper()
	ifp.close()
	chdt = chardet.detect(smi_sgml)
	if chdt['encoding'] != 'UTF-8':
		smi_sgml = unicode(smi_sgml, chdt['encoding'].lower()).encode('utf-8')

	# skip to first starting tag (skip first 0xff 0xfe ...)
	try:
		fndx = smi_sgml.upper().find('<SYNC')
	except Exception, e:
		print chdt
		raise e
	if fndx < 0:
		return False
	smi_sgml = smi_sgml[fndx:]
	lines = smi_sgml.split('\n')
	srt_list = []
	sync_cont = ''
	si = None
	last_si = None
	linecnt = 0
	for line in lines:
		linecnt += 1
		sndx = line.upper().find('<SYNC')
		
		if sndx >= 0:
			
			start_s=None
			start_i=0
			end_s=None
			end_i=0

			m2 = re.search(r'<sync\s([^>]*)>(.*)$', line, flags=re.IGNORECASE)
			if not m2:
				print 'm2 error "%s"' % line
			else :
				syncc = m2.group(1)
				ttt = re.search(r'^([a-zA-Z]+\s*=\s*-{0,1}\d*\s*)+$',syncc, flags=re.IGNORECASE)
				ii = 0
				while  ttt <0:
					print 'error %s' % syncc
					changeorg = None
					changedest = None
					#dbyderror = re.search(r'(([a-zA-Z]*\s*=\s*\d*)([^(0-9)(=)]{1,})(\d{1,}))',syncc, flags=re.IGNORECASE)
					#sbysError = re.search(r'(([a-zA-Z]{1,})([\s0-9]{1,})([a-zA-Z]{1,}\s*=\s*\d*))',syncc, flags=re.IGNORECASE)
					middledError =  re.search(r'(([a-zA-z]{1,}\s*=\s*-{0,1}\d{1,})[\sa-zA-z]{1,}(\d{1,}))\s*',syncc, flags=re.IGNORECASE)
					lastsError = re.search(r'(([a-zA-Z]{1,})\d{1,}(\s*=\s*[-0-9]{1,}))',syncc, flags=re.IGNORECASE)
					firstsError = re.search(r'([\d]{1,}([a-zA-Z]{1,}\s*=\s*[-0-9]{1,}))',syncc, flags=re.IGNORECASE)
					lastdError = re.search(r'(([a-zA-Z]{1,}\s*=\s*)(-{0,1}\d{1,})[^\d\s]{1,})',syncc, flags=re.IGNORECASE)
					firstdError = re.search(r'(([a-zA-Z]{1,}\s*=\s*[-]{0,1})[^-\d\s]{1,}(-{0,1}\d{1,}))',syncc, flags=re.IGNORECASE) 
					#firstdError = re.search(r'(([a-zA-Z]{1,}\s*=\s*)[^-\d\s]{1,}(-{0,1}\d{1,}))',syncc, flags=re.IGNORECASE) 


					if middledError:
						changeorg = middledError.group(1)
						changedest = '%s%s' % (middledError.group(2),middledError.group(3))
						
					if lastsError:
						changeorg = lastsError.group(1)
						changedest = '%s%s' % (lastsError.group(2) , lastsError.group(3))
						
					if firstsError:
						changeorg = firstsError.group(1)
						changedest = '%s' % (firstsError.group(2))
						
					if lastdError:
						changeorg = lastdError.group(1)
						changedest = '%s%s' % (lastdError.group(2) , lastdError.group(3))
						
					if firstdError:
						changeorg = firstdError.group(1)
						changedest = '%s%s' % (firstdError.group(2) , firstdError.group(3))
						
					
					
					
					#if msError:
					#	changeorg = msError.group(1)
					#	changedest = '%s%s' % (msError.group(2) , msError.group(3))
						
					#if dbyderror:
					#	changeorg = dbyderror.group(1)
					#	changedest = '%s%s' % (dbyderror.group(2) , dbyderror.group(4))
					#if sbysError:
					#	changeorg = sbysError.group(1)
					#	changedest = '%s%s' % (sbysError.group(2) , sbysError.group(4))
					
					
					print 'find = %s, change = %s' % (changeorg,changedest)
					
					desttt = re.sub (changeorg,changedest,syncc)
					
					print 'changed %s' % desttt
					
					syncc = desttt
					ttt = re.search(r'^([a-zA-Z]+\s*=\s*-{0,1}\d*\s*)+$',syncc, flags=re.IGNORECASE)
					
					ii = ii+1
					if ii>100 :
						return False
					
						
				start_s = re.search(r'start\s*=\s*(-{0,1}\d*)', syncc, flags=re.IGNORECASE)
				if start_s:
					start_i = long(start_s.group(1))
					if start_i<0L:
						start_i=0L
				end_s = re.search(r'end\s*=\s*(-{0,1}\d*)', syncc, flags=re.IGNORECASE)
				if end_s:
					end_i=long(end_s.group(1))
					if end_i<0L:
						end_i=0L
			#m = re.search(r'<sync\s+start\s*=\s*(\d+)>(.*)$', line, flags=re.IGNORECASE)
			#print 'g0 "%s"' (m2.group(0))
			#if not m:
				#print ('Invalid format tag of <Sync start=nnnn> with "%s"' % line)
			sync_cont += line[0:sndx]
			last_si = si
			if last_si != None:
				if not last_si.is_end:
					last_si.end_ms = start_i
				last_si.contents = sync_cont
				srt_list.append(last_si)
				last_si.linecount = linecnt
				last_si.is_end = False
				#print '[%06d] m1 %s' % (linecnt, last_si)
				#print '%s' % last_s
			si = smiItem()
			if end_s != None:
				si.start_ms = start_i				
				si.end_ms = end_i
				sync_cont = m2.group(2)
				si.is_end = True
			else:
				si.start_ms = start_i
				sync_cont = m2.group(2)
				si.is_end = False
			
			
			
			
			
			#sync_cont += line[0:sndx]
			#last_si = si
			#if last_si != None:
				#last_si.end_ms = long(m.group(1))
				#last_si.contents = sync_cont
				#srt_list.append(last_si)
				#last_si.linecount = linecnt
				#print '[%06d] %s' % (linecnt, last_si)
			#sync_cont = m.group(2)
			#si = smiItem()
			#si.start_ms = long(m.group(1))
		else:
			sync_cont += line
			
	ofp = open(srt_file, 'w')
	ndx = 1
	for si in srt_list:
		si.convertSrt()
		if si.contents == None or len(si.contents) <= 0:
			continue
		#print si
		sistr = '%d\n%s --> %s\n%s\n\n' % (ndx, si.start_ts, si.end_ts, si.contents)
		#sistr = unicode(sistr, 'utf-8').encode('euc-kr')
		ofp.write(sistr)
		ndx += 1
	ofp.close()
	return True
	
def FixType(smi_file):
	s = open(smi_file)
	buf = s.read()
	s.close()
	lines = buf.split('\n')
	
	findSync = False
	for line in lines:
		sndx = line.upper().find('<SYNC')
		if sndx>=0:
			findSync = True
	
	findSrt = False
	
	if not findSync:
		for line in lines:
			find = re.search(r'^(\d*)', line, flags=re.IGNORECASE)
			if find:
				findSrt = True
				break;
	
	if findSrt:
		rndx = smi_file.rfind('.')
		srt_file = '%s.srt' % smi_file[0:rndx]
		d = open(srt_file,'w')
		d.write(buf)
		d.close()
		return True
	return False


def CopyFile2(srt,des):
	s = open(srt)
	buf = s.read()
	s.close()
	
	d = open(des,'w')
	d.write(buf)
	d.close()
	return True



if __name__ == '__main__':

	pwd='/videos'
	
	for path, dirs, files in os.walk(pwd):
		for file in files:
			if os.path.basename(path) == 'smi_backup':
				continue
			if os.path.splitext(file)[1].lower() == '.smi':
				print os.path.join(path,file)
				if convertSMI(os.path.join(path,file)):
					print "Converting <%s> OK!" % os.path.join(path,file)
					if not os.path.exists(os.path.join(path,'smi_backup')):
						os.makedirs(os.path.join(path,'smi_backup'))
					CopyFile2(os.path.join(path,file),os.path.join(path,'smi_backup',file)) 
					os.remove(os.path.join(path,file))
				else:
					if not os.path.exists(os.path.join(path,'smi_backup')):
						os.makedirs(os.path.join(path,'smi_backup'))
					CopyFile2(os.path.join(path,file),os.path.join(path,'smi_backup',file))
					changeType=FixType(os.path.join(path,file))
					if changeType:
						print "smi->srt"
						os.remove(os.path.join(path,file))
					else :
						print "Failure <%s> " % os.path.join(path,file)
					 
				
	print "DONE"