#=======================================================================
#==========================Neural network training======================
#=======================================================================
import os
import numpy as np
import theano
import theano.tensor as T
import gensim.models
import gc
import random
#=========================Global declarations============================
sentences = [] # All the sentences
line = []
splitList = []
dicRelEntity = {}
entityVecDict={}
epsilon = np.float64(0.01)
tensorSlices = 4
dimB = 100 # dimension of B
dimA = 200 # dimension of A
dimE = 100 # dimension of E
dimU = 1 # dimension of U
regparam=0.0001
corTriples=10
totalPasses = 20
AdaA = 0
AdaB = 0
AdaU = 0
AdaE1 = 0
AdaE2 = 0
AdaEC = 0

#=======================================================================
#Function Name : createGensimModel
#Input : corpusFileName
#Output : Sets globally declared gensim word2vec model
#Functionality : Creates word2vec gensim model for relation
#            The triplets file for relation is taken for model creation
#=======================================================================
def createGensimModel(corpusFileName):
    global model
    # f = open(corpusFileName,'r')
    f=open(os.path.join('../../DATA/NeuralNetworkData/relation',corpusFileName),"r")
    localDict = {}
    for line in f :
        splitList = line.replace('\n','').split('\t')
        for item in splitList:
            if entityVecDict.has_key(item):
                continue
            else:
                localDict[item] = 0
        sentences.append(splitList)

    model = gensim.models.Word2Vec(sentences, min_count=1)

    return localDict

#=======================================================================
#Function Name : createGensimModelNew
#Input : corpusFileName
#Outputs : Sets globally declared gensim word2vec model
#          Returns localDict(new entities encountered)
#Functionality : Creates word2vec gensim model for relation
#               Model is built on raw data from wikipedia
#=======================================================================
def createGensimModelNew(corpusFileName):
    global model
    f=open(os.path.join('../../DATA/NeuralNetworkData/relation',corpusFileName),"r")
    localDict = {}
    localEntities = []
    listEntities = []
    totalData = []
    for relLine in f :
        splitRelList = relLine.replace('\n','').split('\t')

        try :
            fent=open(os.path.join('../../DATA/NeuralNetworkData/wikiData',splitRelList[0]),"r") #some folder name
            line = fent.readline()
            while line:
               # print "fent",fent,len(fent)
                if splitRelList[0] in line or splitRelList[2] in line :
                    splitList = line.replace('\n','').split(' ')
                    for item in splitList:
                        if entityVecDict.has_key(item):
                            continue
                        else:
                            localDict[item] = 0
                    totalData.append(splitList)
                line = fent.readline()
            fent.close()
        except:
            # print "in catch",splitRelList
            totalData.append(splitRelList)
        #break
    # for item in totalData:
    #     print item
    model = gensim.models.Word2Vec(totalData, min_count=1)
    return localDict

#=======================================================================
#Function Name : fillEntityVecDictionary
#Input : localDict
#Output : set globally declared entityVecDict
#Functionality :Fills dictionary where key is word in string form and
#               value is vector representating the word
#=======================================================================
def fillEntitryVecDictionary(localDict):
    global model
    print "Filling the dictionary"
    # for item in dictVocab.keys():
    for item in localDict.keys():
        if not entityVecDict.has_key(item):
            entityVecDict[item] = getEntityVector(item)
    print "Filled dictionary"
    return



#============================================================================
#Function Name : build_model
#Input : A,B,U,entity1,entity2,entityCorrupted,num_passes=10, print_loss=True
#Output : A,B,U,lossValue
#Functionality :Builds NN for specific relation
#               It takes original triplet and corrupted one as input
#============================================================================
def build_model(A,B,U,entity1,entity2,entityCorrupted,num_passes=10, print_loss=True):
    global AdaA,AdaB,AdaE1,AdaE2,AdaEC,AdaU
    tempArr = np.zeros((dimA),dtype="float64")
    tempArr1 = np.zeros((dimA),dtype="float64")
    for j in range(0, num_passes):
        E1 = getEntityVectorFromDict(entity1)
        E2 = getEntityVectorFromDict(entity2)
        rowCnt = 0
        for i in E1:
            tempArr[rowCnt] = i
            rowCnt += 1

        for i in E2:
            tempArr[rowCnt] = i
            rowCnt += 1
        E1E2 = tempArr

        EC = getEntityVectorFromDict(entityCorrupted)
        rowCnt = 0
        for i in E1:
            tempArr1[rowCnt] = i
            rowCnt += 1

        for i in EC:
            tempArr1[rowCnt] = i
            rowCnt += 1
        E1EC = tempArr1

        Adash,Bdash,Udash,E1dash,E2dash,ECdash = calculateGradients(A.eval(),B.eval(),U.eval(),E1,E2,E1E2,EC,E1EC)

        #update parameters
        A.set_value (A.get_value(return_internal_type = True,borrow = True) - epsilon * Adash)
        B.set_value (B.get_value(return_internal_type = True,borrow = True) - epsilon * Bdash)
        U.set_value (U.get_value(return_internal_type = True,borrow = True) - epsilon * Udash)
        E1 =  E1 - epsilon * E1dash
        E2 =  E2 - epsilon * E2dash
        EC = EC - epsilon * ECdash


        #update adagrad parameters
        # AdaA = Adash.dot(T.transpose(Adash))

        # AdaA += np.multiply(Adash,Adash.transpose())
        entityVecDict[entity1] = E1
        entityVecDict[entity2] = E2
        entityVecDict[entityCorrupted] = EC
        lossValue = lossFunction(A.eval(),B.eval(),U.eval(),E1,E2,E1E2,EC,E1EC)
        # print "At iteration ",j," loss is : ",lossValue

    #return loss
    return A,B,U,lossValue

#===================================================================================
#Function Name :getEntityVectorFromDict
#Input : ent (in form of string)
#Output : 100 dimentional vector representing entity
#Functionality : It returns vector of entity.
#    If we already have entity representation with us function will return the same.
#    Otherwise it will try to get it from cretaed gensim model.
#    If model doesn't have the entity then it is randomly initialized
#===================================================================================
def getEntityVectorFromDict(ent):
    global model
    if not entityVecDict.has_key(ent):
        entSplit=ent.split(" ")
        if len(entSplit) > 1 :
            # print "Averaging  : ",ent
            myVec = np.zeros((dimE),dtype="float64")
            for e in entSplit:
                if entityVecDict.has_key(e):
                    # v = getEntityVector(e)
                    v = entityVecDict[e]
                else:
                    try:
                        # print "initializing from model"
                        v = getEntityVector(e)
                    except:
                        # print "randomly initilizing word : ",e
                        v = np.random.rand(dimE).astype('float64')



                myVec = np.add(myVec,v)
            entityVecDict[ent] = myVec/(len(entSplit)*1.0)
        else:
            # print "randomly initilizing entity: ",ent
            entityVecDict[ent]  =  np.random.rand(dimE).astype('float64')
    return entityVecDict[ent]

#===================================================================================
#Function Name :getEntityVector
#Input : ent (in form of string)
#Output : 100 dimentional vector representing entity
#Functionality : It returns vector of entity from gensim word2vec model.
#===================================================================================
def getEntityVector(ent):
    global model
    # print model
    return model[ent]

#===================================================================================
#Function Name :calculateGradient
#Input : list of relations
#Output : Trained NN parameters for all relations in input relation list
#Functionality :Function iterates over every triplet of every relation and trains NN
#===================================================================================
def calculateGradient(relationList):

    #loop for each relation
    for relation in relationList:
        print "For relation : ",relation
        loss  = 0

        # localDict = createGensimModel(relation)
        localDict = createGensimModelNew(relation)
        #print "local dict",localDict

        fillEntitryVecDictionary(localDict)

        entityList,tripleDict=populateTripleList(relation)
        A = theano.shared(np.random.randn(tensorSlices, dimA).astype('float64'), name='A',borrow=True)
        B = theano.shared(np.random.randn(tensorSlices,dimB, dimB).astype('float64'), name='B',borrow=True)
        U = theano.shared(np.random.randn(dimU,tensorSlices).astype('float64'), name='U',borrow=True)
        print "training started"

        #Loop for total number of passes
        for iterationCount in range(0,totalPasses):

            loss=0
            #loop for each triplet in relation
            for triple in tripleDict.keys():


                triple=triple.split("\t")
                # print "original",triple,"\n\n"
                m=0
                corruptedList=[]

                #loop for choosing random entitites for corruption
                while m<min(corTriples,len(entityList)):
                    # print "gathering corrupted triples"
                    index=random.randint(0,len(entityList)-1)
                    if entityList[index] not in corruptedList:
                        corruptedList.append(entityList[index])
                        m+=1

                #loop for each corrupted triplet
                for entityCorrupted in corruptedList:
                    corruptedTriple=triple[0]+"\t"+triple[1]+"\t"+entityCorrupted
                    # print "for a corrupted triple"
                    if tripleDict.has_key(corruptedTriple):
                        # print "continue","\n"
                        continue
                    else:
                        # print "corrupted",corruptedTriple,"\n"

                        A,B,U,tempLoss = build_model(A,B,U,triple[0],triple[2],entityCorrupted,10,True)
                        #increament loss
                        loss += tempLoss
                        # corruptedCount+=1

        #print iteration number , loss
            print "At iteration ",iterationCount," loss is : ",loss
            # if loss==0:
            #     break
        #end loop

        #Dump relation specific NN parameters (A,B,U) to file

        #Dump A
        fpparams=open(os.path.join('../../DATA/NeuralNetworkData/NNParameters',relation ),"w")
        tempArr = A.eval()
        for i in range (0,tensorSlices):
            for j in range(0,dimA):
                fpparams.write(str(tempArr[i][j]))
                fpparams.write(" ")
            fpparams.write("\n")
        fpparams.write('\n')
        fpparams.write('\n')

        #Dump B
        tempArr = B.eval()
        for slice in range(0,tensorSlices):
            for i in range (0,dimB):
                for j in range(0,dimB):
                    fpparams.write(str(tempArr[slice][i][j]))
                    fpparams.write(" ")
                fpparams.write("\n")
            fpparams.write('\n')
        fpparams.write('\n')

        #Dump U
        tempArr = U.eval()
        for i in range (0,dimU):
            for j in range(0,tensorSlices):
                fpparams.write(str(tempArr[i][j]))
                fpparams.write(" ")
            fpparams.write("\n")
        fpparams.write('\n')
        fpparams.write('\n')

        fpparams.close()
        
        print "Dumped uptil relation", relation
        #dump all entity vectors
        fpent=open('../../DATA/NeuralNetworkData/EntityVectors',"w")
        for ent in entityVecDict.keys():
                fpent.write("$$$$")
                fpent.write(ent)
                fpent.write("##")
                fpent.write(str(entityVecDict[ent]).replace("'","").replace('[',"").replace(']',"").replace('  '," "))
        fpent.write("$$$$")
        fpent.close()

#===================================================================================
#Function Name :readRelationFile
#Input :
#Output : Relation list
#Functionality : reads relationcount.txt and populated relationList
#              Noe relationList have all relations sorted by triplet count
#===================================================================================
def readRelationFile():
    fp=open("../../DATA/NeuralNetworkData/relationcount.txt","r")
    relationList=fp.read()
    relationList=relationList.split("\n")
    return relationList

#===================================================================================
#Function Name :populateTripleList
#Input : relation name
#Output : entityList, tripleDict
#Functionality : reads all triplets of specific relation
#                and populates entityList and tripletsDict
#===================================================================================
def populateTripleList(file):
    fprelation=open(os.path.join('../../DATA/NeuralNetworkData/training',file),"r")
    fpentity=open(os.path.join('../../DATA/NeuralNetworkData/entity',file),"r")
    tripleDict={}
    entityList=[]
    for line in fprelation:
        line=line.replace("\n","")
        tripleDict[line]=0
    for entity in fpentity:
        entity=entity.replace("\n","")
        entityList.append(entity)
    return entityList,tripleDict

#===================================================================================
#==========================Theano Function definitions==============================
#===================================================================================

#variables declaration
ATemp = T.matrix('ATemp')
BTemp = T.tensor3('BTemp')
UTemp = T.matrix('UTemp')
E1Temp = T.vector('E1Temp')
E2Temp = T.vector('E2Temp')
E1E2Temp = T.vector('E1E2Temp')
ECTemp = T.vector('ECTemp')
E1ECTemp = T.vector('E1ECTemp')

#Definition of scoring function
score = UTemp.dot(T.tanh(E1Temp.dot(BTemp).dot(T.transpose(E2Temp))+ ATemp.dot(E1E2Temp)))
scoringFunction = theano.function([ATemp,BTemp,UTemp,E1Temp,E2Temp,E1E2Temp],score)

#Definition of loss function

#calculated score of corrupted triplet to calculate loss
scoreCorrupted =UTemp.dot(T.tanh(E1Temp.dot(BTemp).dot(T.transpose(ECTemp))+ ATemp.dot(E1ECTemp)))
loss = T.largest(0,(1- (UTemp.dot(T.tanh(E1Temp.dot(BTemp).dot(T.transpose(E2Temp))+ ATemp.dot(E1E2Temp))))+ (UTemp.dot(T.tanh(E1Temp.dot(BTemp).dot(T.transpose(ECTemp))+ ATemp.dot(E1ECTemp))))+regparam*(T.sum(ATemp**2)+T.sum(BTemp**2)+T.sum(UTemp**2))/3))
lossFunction = theano.function([ATemp,BTemp,UTemp,E1Temp,E2Temp,E1E2Temp,ECTemp,E1ECTemp],loss)

#Defining gradients
dA = T.grad(T.sum(loss),ATemp)
dB = T.grad(T.sum(loss),BTemp)
dU = T.grad(T.sum(loss),UTemp)
dE1 = T.grad(T.sum(loss),E1Temp)
dE2 = T.grad(T.sum(loss),E2Temp)
dEC = T.grad(T.sum(loss),ECTemp)

#Definition of function to return gradients
calculateGradients = theano.function([ATemp,BTemp,UTemp,E1Temp,E2Temp,E1E2Temp,ECTemp,E1ECTemp], [dA,dB,dU,dE1,dE2,dEC])

#===================================================================
#=========================Main function ============================
#===================================================================

if __name__ == "__main__":
    #===========Reading all relations and their count===============
    # createGensimModel('corpus')
    # fillEntitryVecDictionary()
    #===========Reading all relations and their count================
    relationList=[]

    noofrelations=raw_input("Please enter the no of relations you want to train : ")
    for i in range(0,int(noofrelations)):
        name=raw_input("Please enter the relation which you want to train(see relationcount.txt) : ")
        relationList.append(name) #remove this

    # print relationList
    #================Neural Network traininig=======================
    calculateGradient(relationList)
    # localDict=createGensimModelNew("state")
    # print len(localDict)
    # fillEntitryVecDictionary(localDict)
    # print entityVecDict['Heath']
    # entityVecDict["kajfg"]=['8.7','6256']
    # getEntityVectorFromDict('rahul')

