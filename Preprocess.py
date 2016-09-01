#==============================================================================
#========================== Neural network Preprocessing ======================
#== This will generate all the files required for training and testing ========
#==============================================================================

import os
import math
import random
import copy
trainpercent=0.7

#=======================================================================
#Function Name : createFinalFiles
#Input :
#Output : Outputs all the files required for training as well as testing
#Functionality : Read all the triplets from data files and creates data
#                for training as well as testing. User will be prompted
#                'trainpercent' that will decide amount of data to be
#                 given for training and testing.
#=======================================================================
def createFinalFiles():
    fileList=os.listdir("output")
    for file in fileList:
        fp=open(os.path.join('../../DATA/NeuralNetworkData/output',file),"r")
        fp1=open(os.path.join('../../DATA/NeuralNetworkData/final',file),"w")
        for line in fp:
            line=line.replace("\n","").split("\t")
            # print line
            temp=line[1].rsplit(".")
            # print line[0],temp[-1],line[2]
            fp1.write(line[0]+"\t"+temp[-1]+"\t"+line[2])
            fp1.write("\n")
        fp1.close()
        fp.close()

#=======================================================================
#Function Name : createRelationFiles
#Input :
#Output : Outputs relations for training as well as testing
#Functionality : Read all triples and seperate relations for training
#                as well as testing'
#=======================================================================
def createRelationFiles():
    relationDict={}
    fileList=os.listdir("../../DATA/NeuralNetworkData/final")
    no=0
    for file in fileList:
        no+=1
        fp=open(os.path.join('../../DATA/NeuralNetworkData/final',file),"r")
        for line in fp:
            line=line.replace("\n","").split("\t")
            # print line
            if relationDict.has_key(line[1]):
                # print "haskey"
                relationDict[line[1]].write(line[0]+"\t"+line[1]+"\t"+line[2])
                relationDict[line[1]].write("\n")
            else:
                # print "creating"
                relationDict[line[1]]=open(os.path.join('../../DATA/NeuralNetworkData/relation',line[1]),"w")
                relationDict[line[1]].write(line[0]+"\t"+line[1]+"\t"+line[2])
                relationDict[line[1]].write("\n")

#=======================================================================
#Function Name : createEntityFiles
#Input :
#Output : Outputs entities for training as well as testing
#Functionality : Read all triples and seperate entities.
#=======================================================================
def createEntityFiles():
    fileList=os.listdir("../../DATA/NeuralNetworkData/relation")
    for file in fileList:
        entityDict={}
        fp=open(os.path.join('../../DATA/NeuralNetworkData/relation',file),"r")
        fp1=open(os.path.join('../../DATA/NeuralNetworkData/entity',file),"w")
        for line in fp:
            line=line.replace("\n","").split("\t")
            if entityDict.has_key(line[2]):
                continue
            else:
                entityDict[line[2]]=0
                fp1.write(line[2])
                fp1.write("\n")
        fp.close()
        fp1.close()

#=======================================================================
#Function Name : createTrainTestFiles
#Input :
#Output : Outputs all the training and testing files
#Functionality : Geneates all training and testing files
#=======================================================================
def createTrainTestFiles():
    fileList=os.listdir("../../DATA/NeuralNetworkData/relation")
    fp2=open("../../DATA/NeuralNetworkData/testing","w")
    for file in fileList:
        tripleList=[]
        fp=open(os.path.join('../../DATA/NeuralNetworkData/relation',file),"r")
        fp1=open(os.path.join('../../DATA/NeuralNetworkData/training',file),"w")
        for line in fp:
            tripleList.append(line)
        fp.close()
        #print tripleList
        trainLength=math.ceil(len(tripleList)*trainpercent)
        #print "trainLength",trainLength
        i=0.0
        while i < trainLength:
            no=random.randint(0,len(tripleList)-1)
            triple=copy.deepcopy(tripleList[no])
            del tripleList[no]
            #print triple
            fp1.write(triple)
            i+=1
        fp1.close()
        for testitem in tripleList:
            fp2.write(testitem)
    fp2.close()

#=========================================================================
#Function Name : getTopRelations
#Input :
#Output : Outputs all relations in deceasing arder of their triplet count
#Functionality : Output all the triples in decreasing order of triple count
#==========================================================================
def getTopRelations():
    fileList=os.listdir("../../DATA/NeuralNetworkData/relation")
    global totalRelcount
    totalRelcount={}
    for file in fileList:
        fp=open(os.path.join('../../DATA/NeuralNetworkData/relation',file),"r")
        no=0
        for line in fp:
            no+=1
        totalRelcount[file]=no

#===========================================================#
#==================== Main starts Here =====================#
#===========================================================#
# createFinalFiles()
# createRelationFiles()

trainpercent = float(raw_input("Enter amount data to be given for training (in the range 0.1 to 0.9) : "))

createEntityFiles()
getTopRelations()
list=sorted(totalRelcount.items(), key=lambda x: x[1],reverse=True)
fpw=open("../../DATA/NeuralNetworkData/relationcount.txt","w")
for item in list:
    fpw.write(str(item).replace("(","").replace(")","").replace("'",""))
    fpw.write("\n")

#Call train files method
createTrainTestFiles()

print "Preprocessing done.."
