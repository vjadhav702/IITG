#This program is used to get entity from freebase and extract properties of the entities. Finally save it in a file in the form of Entity - Relation - Entity triples
import urllib.request as req
import requests
import json
import os


http_proxy  = "http://username:password@202.141.80.19:3128"
https_proxy  = "https://username:password@202.141.80.19:3128"
ftp_proxy   = "ftp://username:password@202.141.80.19:3128"

proxyDict = {
              "http"  : http_proxy,
              "https" : https_proxy,
              "ftp"   : ftp_proxy
            }


# file containing mids of all the entities of person/person domain of freebase
file= open('./../../DATA/SampleData/mids.txt')
listFiles=[]

#line = file.readline()
max=20000000
proxies={}
	


badKeys=["ns:common.topic.alias","ns:common.topic.description","ns:common.topic.image","ns:common.topic.topic_equivalent_webpage","ns:type.object.key","ns:type.object.type","ns:rdf:type","ns:type.object.name","rdfs:label"]


skiplistc2=[]


#this function return names of entity provided the url of the freebase
def getEntityNameFromUrl(identity):
	try:
		newidentity = str(identity)
		newidentity=newidentity.replace('.','/').replace('ns:','')
		

# EACH FREEBASE QUERY REQUIES AN API KEY
		url = "https://www.googleapis.com/freebase/v1/mqlread?key=AIzaSyBnJQP44z6ZcwnhMrzFJirbItNMjgyL8T8&query=[{\"mid\":\"/"  +newidentity+ "\"" +",%22name%22:%20null}]"
		
		#print (url)
		#print js
		response = requests.get(url,proxies=proxyDict);
		newText = str(response.content,'utf-8')
		newText = newText.replace("\n",'')

		#print (newText)
		js = json.loads(newText)
		print (js)
		name = js['result'][0]['name']

		#print (name)
		return name
	except:
		print (" COULT NOT RETRIEVE")
		return ""


#this functions parses the entity file for a particular mid and extracts its information  and saves it in a triple form
def create(name):
	skiplistc2=[]
	#view-source:https://www.googleapis.com/freebase/v1/mqlread?query=[{mid:/ns:m/0hq82,%22name%22:%20null}]
	#view-source:https://www.googleapis.com/freebase/v1/mqlread?query=[{%22mid%22:%20%22/m/01wz6kq%22,%22name%22:%20null}]
	#for name in listFiles:
	entitiesFile =open(os.path.join('./../../DATA/SampleData/freebase_entity_processed/'+name),'w')
	e1Id = name
	e1Name = getEntityNameFromUrl(e1Id)	
	print ("READY TO CREATE" + e1Name)
	#print (name)
	if(len(e1Name) <1):
		print (" COULD NOT OBTAIN KEY NAME for "+e1Id)
		return
		#continue
	else:
		entitiesFile =open(os.path.join('./../../DATA/SampleData/freebase_entity_processed/'+name),'w')
		print ("FILENAME ",name)
		#if('m.' in col3):
		file = open(os.path.join('./../../DATA/SampleData/freebase_entity/'+name),'r')
		#print ("here")
		line = file.readline()
		#print(line)
		skip = 6
		maxlines=500000
		while line and maxlines>0:
			#print (line)
			maxlines-=1
			if( skip>=0):
				#print (line)
				skip-=1
				line = file.readline()
				continue
				#continue
			splittext = line.split("    ")
			col1=splittext[0]
			col2=splittext[1]
			col3=splittext[2]
			col3=col3.replace('\n','')
			col3=col3.replace(';','')
			#print (col1,col2,col3)
		
			triplet = e1Name+ "\t"
			if(col2 not in badKeys and col2 not in skiplistc2):
				if('wikipedia' not in col2):
					if('ns:' in col3):
						print (col2,col3)
						if('m.' in col3):
							Namee1 =getEntityNameFromUrl(col3)
						
							if(not(Namee1) or 	len(Namee1) <1):
								print (" COULD NOT OBTAIN KEY NAME for::: "+col3)
								skiplistc2.append(col2)
								None
							else:
								triplet+=col2+"\t"
								triplet+=Namee1+"\n"
								entitiesFile.write(triplet)
								entitiesFile.flush()
								print ("written to file")
				
			#print (line)
			line = file.readline()
	entitiesFile.close()
	
	
line=file.readline()


# read all the entities and fetch their complete freebase triple from internet. This functions saves a  file for each entity .

while line and max >=0:	
	query = line.replace('\n','')
	query=query[1:]
	pathQuery = query.replace('/','.')	
	
	filePath = "./../../DATA/SampleData/freebase_entity/"+pathQuery
	print (filePath)
	fileout = open(os.path.join('./'+filePath),"wb")
	listFiles.append(query)
	max-=1
	#print col1,"\n"
# sends query to freebase , download it and save it for further processing by create function
	url = "https://www.googleapis.com/freebase/v1/rdf/" + query+ "?key=AIzaSyBnJQP44z6ZcwnhMrzFJirbItNMjgyL8T8"
	print (url)	

	if('http' in url):	
		#print (url)
		response = requests.get(url,proxies=proxyDict);

		string = (response.content)
		fileout.write(string)
		fileout.close()				
	create(pathQuery)
	line= file.readline()
	

