import sys
import nltk
from nltk.corpus import wordnet as wn
nltk.data.path.append('./nltk_data/')

#checks to see if a word has any senses and is a noun, if so we take it on, if not we ignore it
def senseEmp(word):
    global unknownWords
    global usedWords
    
    try :
        senses=wn.synsets(word, pos='n')
        #print 'Working on word', word
   # print(senses)
    except UnicodeDecodeError:
        senses=[]
    if not senses:
        unknownWords.append(word)
 #       print 'There are no senses here'
        return senses
    else:
        i=0
        while i < len(senses) :
            if senses[0].lemmas()[0].name() != senses[i].lemmas()[0].name() :
                senses.remove(senses[i])
            else :
                i+=1
        usedWords.append(word)
        #print senses
        return senses



#checks to see if a word and another a word or equal or related by hyponym, synonym, hypernym or antonym
#word1 is the actual word, while word2 is the synset
def wordRelate(word1, word2):
    global match
    global missedSenses
    join1=False
    antonyms=[]
    match=None
    missedSenses=[] #This list is to keep track of the missed senses that occur for each word throughout the document
    for i in range(0, len(word2)):
#        print word2[i], word1
        #checks to see if the words are identical
        if word2[i]==word1:
            join1=True
            match=word2[i]
            break
        #checks to see if the words have a hypernym relationship
        for k in range(0, len(word2[i].hypernyms())):
            if word2[i].hypernyms()[k]==word1:
                join1=True
                match=word2[i]
                break
        #checks to see if the words have a hyponum relationship
        for k in range(0, len(word2[i].hyponyms())):
            if word2[i].hyponyms()[k]==word1:
                join1=True
                match=word2[i]
                break
        #checks to see if the words have a relationship with synonyms
        for k in range(0, len(word2[i].lemmas())):
            if word2[i].lemmas()[k].antonyms() :
                for m in range(0, len(word2[i].lemmas()[k].antonyms())):
                    #This is to get the list of antonyms
                    antonyms.append(word2[i].lemmas()[k].antonyms()[m])
                    if word2[i].lemmas()[k]==word1:
                        match=word2[i]
                        join1=True
                        break
                    if join1: break
        #checks to see if equal to any of the antonyms
        for k in range(0, len(antonyms)):
                #print antonyms[k].name()
                #print word1[l].lemmas()[0].name()
            for m in range(0, len(word1.lemmas())):
                if antonyms[k].name()==word1.lemmas()[m].name() :
                    join1=True
                    match=word2[i]
                    break
                if join1 : break
            if join1 : break
        missedSenses.append(i)
#    print missedSenses
    return join1


#eliminating the helper chains (which did not help)
def elimHelper():
    global allSenses
    for i in range (0, len(allSenses)):
        k=0
        while k < len(allSenses[i]) :
            if (usedWords.count(allSenses[i][k].lemmas()[0].name()) == 0 ):
                allSenses[i].remove(allSenses[i][k])
            else:
                k+=1
    while [] in allSenses : allSenses.remove([])



#adds the different senses of a word to the appropiate chains
def add2chains(word):
    global allSenses
    global match
    global missedSenses
    join=False
  #  print len(allSenses)
    #If it is the first word we make chains for all the senses of that word
    if len(allSenses) == 0 :
        for i in range(0, len(word)):
            chain=[]
            chain.append(word[i])
            allSenses.append(chain)
    #If not the first word, then it checks through each of the chains then adds the appropiate sense of the word to the appropiate chain
    else:
   #     print 'senses chain list greater than 3'
        for i in range(0, len(allSenses)):
            chain=allSenses[i]
            for k in range(0, len(chain)):
                if wordRelate(chain[k], word) : 
                    allSenses[i].append(match)
                    join=True
                    break
        #For all the senses that were missed for a word, we make a new chain appropiate for them
        if  missedSenses :
    #        print missedSenses
            for i in range(0, len(missedSenses)):
                chain=[]
                chain.append(word[missedSenses[i]])
                allSenses.append(chain)
            
            

##prints all of the chains made out
def printChains():
    global allSenses
    global usedWords
    for i in range(0, len(allSenses)):
        chain=allSenses[i]
        print ' '
        print 'Chain', i ,':',
        for k in range(0, len(chain)):
            numReps=usedWords.count(chain[k].lemmas()[0].name())
            print chain[k].lemmas()[0].name(), '(', numReps, ')', 




##Chain Eliminater!
def eliminateChains():
    global allSenses
    global usedWords
    global elimChains
    loc=getMaxChainLoc()
    max=getMaxChainVal()
    x=0
    ##Eliminates repeats from the largest chain continuously
    #It should be noted that it only looks at a chain once, the locations of the previous chains are put into a list
    while max != 1 :
        #loops through all different words for that chain and eliminates repeats
        while x < len(allSenses[loc]):
            chain=allSenses[loc]
            repeatsCount=allSenses[loc].count(allSenses[loc][x])
            wordSen=allSenses[loc][x]
            wordnoSen=chain[x].lemmas()[0].name()
            if repeatsCount > 1 :
                while repeatsCount != 1 :
                    allSenses[loc].remove(wordSen)
                    repeatsCount-=1
            #eliminates words from other chains that may have a repeat
            for m in range(0,len(allSenses)) :
                if m!=loc :
                    otherchain=allSenses[m]
                    n=0
                    while n < len(otherchain):
                        if wordnoSen==otherchain[n].lemmas()[0].name() :
                            allSenses[m].remove(otherchain[n])
                        else :
                            n+=1
            
            x+=1
        elimChains.append(loc)
        loc=getMaxChainLoc()
        max=getChainLen(loc)
        #print 'len is ', max
        #print 'loc is ', loc
    #Goes through entire list to eliminate repeats of single sized chains
    for i in range(0, len(allSenses)):
        chain=allSenses[i]
        k=0
        while k < len(chain) :
            wordnoSen=chain[k].lemmas()[0].name()
            repeatsCount=chain.count(chain[k])
            if repeatsCount > 1 :
                while  repeatsCount != 1 :
                    allSenses[i].remove(chain[k])
                    repeatsCount-=1

     #       print wordnoSen
            for m in range(i+1,len(allSenses)) :
                otherchain=allSenses[m]
                n=0
                while n < len(otherchain):
                    if wordnoSen==otherchain[n].lemmas()[0].name() :
                        allSenses[m].remove(otherchain[n])
                    else :
                        n+=1
            k+=1
            
    ##Bye Bye Empty Chains!
    while [] in allSenses : allSenses.remove([])




##returns the location of the maximum Chain length from allSenes
def getMaxChainLoc():
    global elimChains
    global allSenses
    max=0
    loc=0
#x    print elimChains
    for i in range(0, len(allSenses)):
        if len(allSenses[i]) > max and i not in elimChains: 
            max=len(allSenses[i])
            loc=i
    return loc


#returns chain length
def getChainLen(loc):
    global allSenses
    return len(allSenses[loc])


#returns the length of the longest chain
def getMaxChainVal():
    global allSenses
    max=0
    for i in range(0, len(allSenses)):
        if len(allSenses[i]) > max : max=len(allSenses[i])
    return max



if __name__=='__main__':
    global allSenses #manages all the different sense chains
    global unknownWords #Keeps track of words not used in the chaining
    global usedWords  #Keeps track of all the words that we actually used during the chaining
    global elimChains ##This keeps track of the largest chain
    elimChains=[]
    #Requesting input for the file name
    file_name=raw_input('Please enter the name of the file or type in quit: ')
    file_list=[]
    if file_name == "quit":
        sys.exit()
    else:
        try:
            fin=open(file_name)
        except:
            print 'The file requested was not found'
    file_list=fin.read().split(' ')
    #print(file_list)
    usedWords=[]
    unknownWords=[]
    allSenses=[]
    #print ('The first word and last word respectively is:',file_list[0], file_list[len(file_list)-1])
    #loops through all the words of the document and adds them to the appropiate chain
    for i in range(0,len(file_list)):
        word=senseEmp(file_list[i])
        if word :
            add2chains(word)
            #printChains()
    elimHelper() #Helps eliminate irrelivant chains
    eliminateChains() #Eliminates the repeated words from the different chains
    printChains() #prints out all of the chains

    #print(wn.synsets(file_list[4]))
    #print(len(wn.synsets(file_list[4])))
    
