#=======================================================================+
#========================== Hidden Rule Extraction ======================
#=======================================================================+
import numpy as np
import os
import theano
import theano.tensor as T
import random
import gensim.models

#=========================Global declarations============================
dictVocab = {}
sentences = []
tensorSlices = 4
dimB = 100 # dimension of B
dimA = 200 # dimension of A
dimE = 100 # dimension of E
dimU = 1 # dimension of U
corTriples=10
entityVecDict={}
dimE = 100
model=0

relation1=""
relation2=""
testrelation=""

#=======================================================================
#Function Name : loadEntityVectors
#Input :
#Output : populates globally declarted entityVecDict
#Functionality : Reads text file of entity vectors dumped while training
#                and populates entityVecDict
#=======================================================================
def loadEntityVectors():
    fpent=open('../../DATA/NeuralNetworkData/EntityVectors',"r")
    entities = fpent.read().split("$$$$")
    # print entities
    for entity in entities:
        entity = entity.replace("\n","")
        entityAttr = entity.split("##")
        # print entityAttr
        if len(entity)!=0:
            arr = entityAttr[1].split(" ")
            if not entityVecDict.has_key(entityAttr[0]):
                tempArr = np.zeros(dimE)
                j=0
                i=0
                while j<dimE:
                    if len(arr[i])!=0:
                        tempArr[j] =  float(arr[i])
                        j+=1
                    i+=1
                entityVecDict[entityAttr[0]] = tempArr
                # print tempArr
    fpent.close()
    # print entityVecDict
    return


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
            if dictVocab.has_key(item):
                continue
            else:
                dictVocab[item] = 0
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
        #localEntities.append(splitRelList[0])
        #break
        #for entity in localEntities:
        try :
            fent=open(os.path.join('.../../DATA/NeuralNetworkData/wikiData',splitRelList[0]),"r") #some folder name
            for line in fent:

                if splitRelList[0] not in line and splitRelList[2] not in line :
                    continue

                splitList = line.replace('\n','').split(' ')
                for item in splitList:
                    if dictVocab.has_key(item):
                        continue
                    else:
                        dictVocab[item] = 0
                        localDict[item] = 0
                totalData.append(splitList)
        except:
            # print "in catch",splitRelList
            totalData.append(splitRelList)
        #break
    for item in totalData:
        print item
    model = gensim.models.Word2Vec(totalData, min_count=1)
    return localDict

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
            print "Averaging  : ",ent
            myVec = np.zeros((dimE),dtype="float64")
            for e in entSplit:
                if entityVecDict.has_key(e):
                    # v = getEntityVector(e)
                    v = entityVecDict[e]
                else:
                    try:
                        print "initializing from model"
                        v = getEntityVector(e)
                    except:
                        print "randomly initilizing word : ",e
                        v = np.random.rand(dimE).astype('float64')



                myVec = np.add(myVec,v)
            entityVecDict[ent] = myVec/(len(entSplit)*1.0)
        else:
            print "randomly initilizing entity: ",ent
            entityVecDict[ent]  =  np.random.rand(dimE).astype('float64')
    return entityVecDict[ent]


#===================================================================================
#==========================Theano Function definitions==============================
#===================================================================================
ATemp = T.matrix('ATemp')
BTemp = T.tensor3('BTemp')
UTemp = T.matrix('UTemp')
E1Temp = T.vector('E1Temp')
E2Temp = T.vector('E2Temp')
E1E2Temp = T.vector('E1E2Temp')
ECTemp = T.vector('ECTemp')
E1ECTemp = T.vector('E1ECTemp')

#Calculate scoring function
temp1 = E1Temp.dot(BTemp).dot(T.transpose(E2Temp))
temp2 = ATemp.dot(E1E2Temp)
temp3 = temp1 + temp2
temp4 = T.tanh(temp3)
score = UTemp.dot(temp4)
scoringFunction = theano.function([ATemp,BTemp,UTemp,E1Temp,E2Temp,E1E2Temp],score)


#=======================================================================
#Function Name : loadEntityVectors
#Input : relation name
#Output : return NN params (A,B,U) for input relation
#Functionality : Returns NN parameters for specific relation
#        Function reads parameters from text files dumped while training
#=======================================================================
def loadNNParmsForRelation(relation):

    fpparams=open(os.path.join('../../DATA/NeuralNetworkData/NNParameters',relation ),"r")

    parameters = fpparams.read().split("\n\n\n")

    # A = theano.shared(np.random.randn(tensorSlices, dimA).astype('float64'), name='A',borrow=True)
    # B = theano.shared(np.random.randn(tensorSlices,dimB, dimB).astype('float64'), name='B',borrow=True)
    # U = theano.shared(np.random.randn(dimU,tensorSlices).astype('float64'), name='U',borrow=True)
    tempA = np.zeros((tensorSlices, dimA),dtype="float64")
    tempB = np.zeros((tensorSlices,dimB, dimB),dtype="float64")
    tempU = np.zeros((dimU,tensorSlices ),dtype="float64")

    #read A
    # print "A",parameters[0]
    # print "B",parameters[1]
    # print "U",parameters[2]
    # exit()
    AStr = parameters[0].split(" ")
    for i in range(0,tensorSlices):
        for j in range(0,dimA):
           tempA[i][j] = AStr[(i*dimA+j)]

    # print "A"
    # print tempA
    # print AStr
    #read B
    BStr = parameters[1].split(" ")
    for slice in range(0,tensorSlices):
        for i in range(0,dimB):
            for j in range(0,dimB):
                tempB[slice][i][j] = BStr[(slice*dimB*dimB)+i*dimB+j]
    # print "B"
    # print tempB
    # print BStr
    #read U
    UStr = parameters[2].split(" ")
    for i in range(0,dimU):
        for j in range(0,tensorSlices):
           tempU[i][j] = UStr[(i*dimU+j)]
    # print "U"
    # print tempU
    # print UStr
    fpparams.close()
    # A = theano.shared(tempA, name='A',borrow=True)
    # B = theano.shared(tempB, name='B',borrow=True)
    # U = theano.shared(tempU, name='U',borrow=True)


    return tempA,tempB,tempU

#===================================================================================
#Function Name :testTriplet
#Input : triplet
#Output : score of triplet
#Functionality : It returns score of input triplet
#===================================================================================
def testTriplet(triplet,tempA,tempB,tempU):


    A = theano.shared(tempA, name='A',borrow=True)
    B = theano.shared(tempB, name='B',borrow=True)
    U = theano.shared(tempU, name='U',borrow=True)

    # print A
    # print B
    # print U

    # E1 = entityVecDict[triplet[0]]
    # E2 = entityVecDict[triplet[2]]

    E1 = getEntityVectorFromDict(triplet[0])
    E2 = getEntityVectorFromDict(triplet[2])
    tempArr = np.zeros(dimA)
    rowCnt = 0
    for i in E1:
        tempArr[rowCnt] = i
        rowCnt += 1

    for i in E2:
        tempArr[rowCnt] = i
        rowCnt += 1
    E1E2 = tempArr

    score = scoringFunction(A.eval(),B.eval(),U.eval(),E1,E2,E1E2)
    return score


#===================================================================
#=========================Main function ============================
#===================================================================
if __name__ == "__main__":

    #First ask user which hidden relation needs to be scored.
    relation1=raw_input("Enter First(LHS) Relation Name : ")
    relation2=raw_input("Enter Second(RHS) Relation Name : ")
    testrelation=raw_input("Enter Hidden(Transitive) Relation Name : ")

    createGensimModel(testrelation)
    loadEntityVectors()
    tempA1,tempB1,tempU1= loadNNParmsForRelation(relation1)
    tempA2,tempB2,tempU2= loadNNParmsForRelation(relation2)

    # print "A1 matrix",tempA1
    # print "B1 matrix",tempB1
    # print "U1 matrix",tempU1
    # print "A2 matrix",tempA2
    # print "B2 matrix",tempB2
    # print "U2 matrix",tempU2
    tempAcomp=np.add(tempA1,tempA2)
    tempBcomp=np.multiply(tempB1,tempB2)
    tempUcomp=np.add(tempU1,tempU2)

    # print "A matrix",tempAcomp
    # print "B matrix",tempBcomp
    # print "U matrix",tempUcomp
    fptest=open("../../DATA/NeuralNetworkData/testing","r")
    MRR=0
    HITS=0
    no=0

    for line in fptest:
        line=line.replace("\n","")
        triplet=line.replace("\n","").split("\t")
        if triplet[1]==testrelation:
            score=testTriplet(triplet,tempAcomp,tempBcomp,tempUcomp)
            print "Score for original triplet : ",triplet," is ",score
            originalscore=score[0]
            rank=1
            fpcorr=open(os.path.join('../../DATA/NeuralNetworkData/entity',triplet[1]),"r")
            corruptedList=[]
            for  entity in fpcorr:
                entity=entity.replace("\n","")
                corruptedList.append(entity)
            # print corruptedList
            i=0
            trainDict={}
            fptrain=open(os.path.join('../../DATA/NeuralNetworkData/relation',triplet[1]),"r")
            for line in fptrain:
                line=line.replace("\n","")
                if trainDict.has_key(line):
                    continue
                else:
                    trainDict[line]=0
            # print trainDict
            triplet=triplet[0:2]
            while i < corTriples:
                index=random.randint(0,len(corruptedList)-1)
                corentity=corruptedList[index]
                del corruptedList[index]
                triplet.append(corentity)
                # print triplet
                key=triplet[0]+"\t"+triplet[1]+"\t"+triplet[2]
                if not trainDict.has_key(key):
                    score=testTriplet(triplet,tempAcomp,tempBcomp,tempUcomp)
                    print "Score for corrupted triplet : ",triplet," is ",score
                    if score[0]>originalscore:
                        rank+=1
                    i+=1
                else:
                    score=testTriplet(triplet,tempAcomp,tempBcomp,tempUcomp)
                    print "Already present in training",triplet," is ",score
                triplet.pop()
            print "rank of triplet",rank,"\n\n"
            MRR+=1/(rank*1.0)
            if rank<=10:
                HITS+=1
            no+=1
print "The MRR of the relation",testrelation,"is",MRR/no
if corTriples>10:
    print "Hits@10",HITS/(no*1.0)
