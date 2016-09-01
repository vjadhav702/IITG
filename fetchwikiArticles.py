# THIS PROGRAM DOWNLOADS WIKI DATA AND SAVES IT IN ITS FILE ( FOR ALL ENTITIES )
import urllib
import urllib2
from bs4 import BeautifulSoup
import io
import os

path = os.path.join('./../../DATA/SampleData/wikiLinks/')
dirs = os.listdir( path )
outRAWPath = os.path.join('./../../DATA/SampleData/wikiDataFullText/')
outPath = os.path.join('./../../DATA/SampleData/wikiDataParsedText/')

counter1=0
counter2=0
# IF PROGRAM EXCEPTION OCCURS , THE CORRUPTED ENTITIES ARE STORED IN curruptedEntity .
fCurrpted = open("./../../DATA/SampleData/corruptedEntity", "w")
counter = 0

# for all entities downloads wiki articles
for x in dirs :
    counter = counter + 1
    try:
        # continue from here if program crashes , skip counter
        if (counter < 0):
                print("Skipping",counter)
                continue
        print ("Dumping data",x)


        fullPath = path+x
        readWikiUrlFile = open(fullPath,'r')
        wikiLine = readWikiUrlFile.readline()
        wikiLineSplit= wikiLine.split('\t')
        urlWiki = wikiLineSplit[1]
        urlWiki = urlWiki.replace('<','')
        urlWiki = urlWiki.replace('>','')
        urlWiki = urlWiki.replace(';','')

        #print ("my data ===> ",urlWiki)
        print(x)

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

        resource = opener.open(urlWiki)

        #resource = opener.open("https://en.wikipedia.org/wiki/"+x)
        data = resource.read()
        fullOutRawPath = outRAWPath+ x
        f1 = open(fullOutRawPath, 'w')
        f1.write(data)
        f1.close()
	# save in file (entity name)

        #print data
        resource.close()

        '''soup = BeautifulSoup(data, "html.parser")

        #print data
        #raw = nltk.clean_html(soup)
        #testData = soup.p
        #print testData
        test = soup.get_text()
        #test = soup.content()
        #f = open('workfile', 'w')
        parsedFIle = outPath+x
        f = io.open(parsedFIle, 'w', encoding='utf8')
        #f.write(test)
        counter = 0
        for line in test.split("\n"):

            line = line.replace("[edit]", '')

            line = line.replace("[", ' ')

            line = line.replace("]", '')

            if (line.startswith("^")):
                continue

            if (line.startswith("(window.RLQ=")):
                continue

            if "Biography and bibliography[edit]" in line:
                break
            if "References[edit]" in line:
                break

            counter = counter + 1
            if counter < 60:
                continue

            if line == "":
                continue
            #print(line)
            #lineResult = libLAPFF.parseLine(line)
            try:
                f.write(line+"\n")
            except :
                print ("Exception at "+x)'''

    except :
            print("Exception")
            fCurrpted.write(x+"\n")

print ("Done")

#print test
#body = soup.find('body')
#body = soup.findAll(text=True)
#the_contents_of_body_without_body_tags = body.findChildren()
#print soup.find('div',id="bodyContent").p
