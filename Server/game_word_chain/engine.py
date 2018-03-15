import random

class humanEg():
    def humanInput(lastChar):
        print("USER>", lastChar, end=" / ")
        # humanWord = input("")
        return lastChar

    def humanConnectChar(humanInputWord,plusChar):
        humanWord = str(plusChar) + str(humanInputWord)
        return humanWord

    def humanWordDefine(hmWord,dicData):
        for dicWord in dicData:
           if dicWord == hmWord:
                return False
        return True

    def humanUseWord(hmWord,useData):
        for useWord in useData:
            if hmWord == useWord:
                return True
        return False


class computerEg():
    def useWord(lastChar,dicData):
        #마지막글자와 첮번째 글짜가 같은것들을 리스트로 묶기
        canUse = []
        for dicWord in dicData:
            try:
                firstChar = dicWord[0]
            except:
                pass
            if firstChar == lastChar:
                canUse.append(dicWord)
            else:
                continue
        return canUse

    def useAgain(word,useData):
        for use in useData:
            try:
                word.remove(use)
            except:
                pass
        return word

    def selectWord(canUse):
        wordLen = len(canUse)-1
        useWord = canUse[random.randint(0,wordLen)]
        return useWord

    def useDataJoin(word,useData):
        useData = useData.append(word)
        return useData


class defaultEg():
    def getLastChar(word):
        #맨 마지막 단어 구하기
        Len = len(word)
        return word[Len - 1]

    def getFisrtChar(word):
        return word[0]

    