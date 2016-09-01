# This program extracts wiki Data from already dumped wikipedia files of entities.
# preprocessing is done here
import urllib
import urllib2
from bs4 import BeautifulSoup
import io
import os


# list of wiki files
path = os.path.join('./../../DATA/SampleData/wikiDataFullText/')
dirs = os.listdir( path )
outPath = os.path.join('./../../DATA/SampleData/wikiDataParsedText/')
counter1=0
counter2=0

fCurrpted = open("./../../DATA/SampleData/corruptedEntityWiki", "w")
# for all wiki files
for x in dirs :
	try:
		fullPath = path+x
		readWikiUrlFile = open(fullPath,'r')
		wikiLine = readWikiUrlFile.read()
		data = wikiLine
				
		'''wikiLineSplit= wikiLine.split('\t')
		urlWiki = wikiLineSplit[1]
		urlWiki = urlWiki.replace('<','')
		urlWiki = urlWiki.replace('>','')
		urlWiki = urlWiki.replace(';','')

		print "my data ===> ",urlWiki
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this
		resource = opener.open(urlWiki)	
	
		#resource = opener.open("https://en.wikipedia.org/wiki/"+x)
		data = resource.read()
		fullOutRawPath = outRAWPath+ x
		f1 = open(fullOutRawPath, 'w')
		f1.write(data)
		f1.close()

		#print data
		resource.close()'''
		soup = BeautifulSoup(data, "html.parser")
		
		#print data
		#raw = nltk.clean_html(soup)
		#testData = soup.p
		#print testData
		test = soup.get_text()
		

		#test = soup.content()
		#f = open('workfile', 'w')
		parsedFIle = outPath+x
		#print parsedFIle
		#print parsedFIle		
		f = io.open(parsedFIle, 'w', encoding='utf8')
		#f.write(test)
		#print test
		#print "here"		
		counter = 0
		flag =0
		for line in test.split("\n"):
			#print line +"********"							
			#meaniningful data starts from here, till then skip
			if('The topic of this article may not meet Wikipedia' in line ):
				continue
			
			if ('From Wikipedia, the free encyclopedia'  not in line and flag==0):				
				continue
			if ('From Wikipedia, the free encyclopedia' in line and flag==0):				
				flag=1
				line=""
			
			#line = line.replace("[edit]", '')
			

			if (line.startswith("(window.RLQ=")):
				continue
			# this is end of wiki page , skip further
			if "Biography and bibliography[edit]" in line:
				break
			if "References[edit]" in line:	
				break

			line = line.replace("[", ' ')
			
			line = line.replace("]", '')
			if (line.startswith("^")):
				continue
			counter = counter + 1
			#if counter < 60:
			#	continue
		
			if line == "":
				continue
			#print(line)
			#lineResult = libLAPFF.parseLine(line)
			# break if this line comes ,all further text is useless.
			if('Retrieved from "https://en.wikipedia.org/w/index.php' in line):
			#print "line "
				break
			try:
				print line				
				
				f.write(line+"\n")
			except :
				print ("Exception at "+x)
			
	except :
		# in case wiki article is not processed , inform admin
	        fCurrpted.write(x+"\n")
	print ("Done" +fullPath)
	f.close()
	#print test
	#body = soup.find('body')
	#body = soup.findAll(text=True)
	#the_contents_of_body_without_body_tags = body.findChildren()
	#print soup.find('div',id="bodyContent").p
	#print the_contents_of_body_without_body_tags
