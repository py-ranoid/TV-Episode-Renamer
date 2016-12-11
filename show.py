import urllib
import os
import re
import urllib, json

#Change path here
path = ''

try:shows=os.listdir(path)
except OSError:
	print 'Error :\tDirectory not found due to invalid path.\nChange to appropriate directory'
	exit()

for i in xrange(len(shows)):
	print str(i).ljust(2),':',shows[i]
try:show=shows[input('Choose Show Number >> ')]
except IndexError:
	print 'Error :\tShow number index is out of range\n\tTry again with appropriate index'
	exit()

def IMDBid(show):
	params = urllib.urlencode({'t':show})
	ret = urllib.urlopen('http://www.omdbapi.com/?'+params).read()
	js = json.loads(ret)
	return js['imdbID']

def IMDBscraper(html,episode):
	y=html
	for i in xrange(len(y)):
		if y[i][-4:]=='ep'+episode+'"':break
	return y[i+1].split('"')[1]

def getHTML(imid,season):
	html = urllib.urlopen("http://www.imdb.com/title/"+imid+"/episodes?season="+str(season))
	return html.read().split('\n')

def epList(show,season):
	site = 'http://www.omdbapi.com/?'
	data = {'t':show,'Season':season}
	params = urllib.urlencode(data)
	ret = urllib.urlopen(site+params).read()
	js = json.loads(ret)
	eps={}
	try:
		for i in js['Episodes']:eps[int(i['Episode'])]= [i['Title'],i['imdbRating']]
	except:pass
	return eps

def fetchFiles(fpath,season=None):
	if season is None:
		a=os.listdir(fpath)
		s=-1
	else:
		a=os.listdir(fpath)
		s=int(season)
	files={}
	numfiles=len(a)
	for i in a:
		if s==-1:filename=i
		else:filename=i[:-4]
		x=re.findall('[eE]([0-9]+)',filename)
		if x:
			num=int(x.pop())
		else:
			x=re.findall('([0-9]+)',filename)
			while True:
				if not x:print'Unable to identify',i;num=-1;break
				num=int(x.pop())
				skip=[360,720,480,1080,264,265]
				if num not in skip and num >0 and num<=numfiles:
					if num==s:
						if input('Is '+i+' episode '+str(num)+' ? (0 for no) : '):break
					else:break
		files[i]=num
	return files

print '\n\nSeasons available :'
spath=os.path.join(path,show)
seasonList = fetchFiles(spath)

for i in seasonList:
	if seasonList[i]> 0: print seasonList[i],':',i
s=raw_input('Choose season : ')

folderList=[]
temp=map(int,s.split('-'))
if len(temp)==1:folderList.append(seasonList.keys()[seasonList.values().index(temp[0])])
else:
	keys=seasonList.keys()
	vals=seasonList.values()
	for i in range(temp[0],temp[1]+1):
		folderList.append(keys[vals.index(i)])

for folder in folderList:
	season=seasonList[folder]
	print '\n\n Renaming Season',season,'episodes\n'
	fpath=os.path.join(spath,folder)
	os.chdir(fpath)
	files = fetchFiles(fpath,season)
	ep=epList(show,season)
	html=None
	for i in files:
		num=files[i]%100
		try:
			title=ep[num][0]
			if 'Episode' in title:
				raise ValueError
			new=str(num)+'. '+title+' ('+ep[num][1]+')'+i[-4:]
		except:
			try:
				html=getHTML(IMDBid(show),season)
				title=IMDBscraper(html,str(num))
				new=str(num)+'. '+title+i[-4:]
			except Exception as e:
				new=i
		if '/' in new:new='-'.join(new.split('/'))
	   	print i.ljust(80),'---->',new
		os.rename(i,new)
