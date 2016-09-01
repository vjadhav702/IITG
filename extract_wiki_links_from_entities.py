# This program finds out wikipedia links from freebase entity file.
# we have restricted to en.wikipedia  i.e English wikipedia links for the entity
import os, sys

# Open a file
path = os.path.join('./../../DATA/SampleData/freebase_entity/')
dirs = os.listdir( path )
outPath = os.path.join('./../../DATA/SampleData/wikiLinks/')

wiki_field="topic.topic_equivalent_webpage"
wiki_en="en.wikipedia"
alreadyGenPath = os.path.join('./../../DATA/SampleData/freebase_entity_processed/')
counter1=0
counter2=0


# for all entities get their wiki links and dump in a file
for x in dirs :
	if(x[0]=='.'):
		continue
	print ("X",x)
	newPath = path+x
	counter1+=1
	#print newPath
	fileop = open(newPath,'r')
	line = fileop.readline()
	flag=0
	doneWikiID =0
	while line:
		lineText= line.replace('\n','').replace('\r','')
	
		lineSplit =lineText.split("    ")
		
		if(len(lineSplit)==3):
			#print lineSplit
			if(wiki_field in lineSplit[1] and wiki_en in lineSplit[2]):				
				#print lineSplit,"\n"

				# the freebase entity can have multiples wikipedia links , process only English one's
				if(doneWikiID==0):
					counter2+=1
					#print "path",alreadyGenPath+x+"---"
					fPath = alreadyGenPath+x
				
					alreadyFile = open(fPath,"r")
					userNameLine = alreadyFile.readline()	
					splitNameLine = userNameLine.split('\t')
					name = splitNameLine[0]

					file = open(outPath+name,"w")
					file.write(x+"\t"+lineSplit[2])
					
					flag=1
				if(doneWikiID==1):
					counter2+=1
					#print "path",alreadyGenPath+x+"---"
					fPath = alreadyGenPath+x
				
					alreadyFile = open(fPath,"r")
					userNameLine = alreadyFile.readline()	
					splitNameLine = userNameLine.split('\t')
					name = splitNameLine[0]
					print (outPath+name)
					if(not file):
						file = open(outPath+name,"w")
					file.write("\t"+lineSplit[2])
					file.close()
					flag=1
				doneWikiID=1
		line=fileop.readline()	
	if (flag==0):
		# SOME FREEBASE ENTITIES DON'T have wikipedia links , find info manually or dump data from freebase
		print ("NF")		
		notEvaluated=outPath+"notEval/"
		filePath= notEvaluated+x
		file2 = open(filePath,"w")
		file2.write("NOTHING")
		file2.close()
		
print ( counter1,counter2)
#print dirs


