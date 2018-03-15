# -*- coding:utf-8 -*-
# print("""
#
#     *************************[ Rule ]****************************
#     1. DB에 있는 단어만 사용 가능
#     2. DB에 없는 단어를 입력 할 경우,
#        DB에 저장되어 다음 게임에서 사용 가능
#     3. 직접 DB를 수정하고 싶을 경우,
#        word_dictionary_kor.txt파일 수정
#     *************************************************************
#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# """, end="")
from game_word_chain import korean_dictionary_api
from game_word_chain import engine
import time, sys, os


def countdown(n):
    if n == 0:
        print("Please enter a word")
    else:
        print(n)
        time.sleep(1)
        countdown(n-1)

def start(lastChar):
    dicData = []  # 사전목록
    useData = []  # 이미사용된 단어 저장

    try:
        f = open("game_word_chain/db/word_dictionary_kor.txt", "r")
        while True:
            data = f.readline().rstrip('\r\n')
            dicData.append(data)
            if data == "":
                break
    except:
        print("[Error] DB file not found")
        print("[Fail] Loading Word Chain Game ...")

    hmWord = engine.humanEg.humanInput(lastChar)               # 사람이 단어를 입력함
    # hmWord = word_chain.engine.humanEg.humanConnectChar(hmWord,lastChar)  # 사람이 입력 한 단어를 가공함
    hmCanUse = engine.humanEg.humanWordDefine(hmWord,dicData)  # 사람이 입력한 단어가 있는지 확인
    if hmCanUse:
        ### word_dictionary_kor DB에 구성되지 않은 단어 일 경우, word_dictionary_kor DB 추가 ###
        korean = hmWord
        check = korean_dictionary_api.posCheck(korean)
        if check == "true":
            print("[word-chain] '{}'은(는) DB에 구성되지 않은 단어입니다.".format(hmWord))
            print("[word-chain] '{}'이(가) DB에 추가되었습니다. 다음 게임에서 적용됩니다.".format(hmWord))
            f = open("game_word_chain/db/word_dictionary_kor.txt", 'a')
            f.write(hmWord + '\n')
            f.close()
        else:
            print("[word-chain] '{}'은(는) 명사가 아닙니다.".format(hmWord))
            return "not a noun"

    used_word = engine.humanEg.humanUseWord(hmWord,useData)
    if used_word:
        # return "이미 사용한 단어에요, 모피에게 졌어요."
        return "already used words"
    else:
        useData.append(hmWord)
    ### 사람이 입력할것이 완료됨 ###

    ### 컴퓨터의 시작 ###
    lastChar = engine.defaultEg.getLastChar(hmWord)
    comWord = engine.computerEg.useWord(lastChar,dicData)
    if comWord == []:
        print("[word-chain] Moppy : ", lastChar[-1])
        print("[word-chain] DB에 {}(으)로 시작하는 단어가 없을 경우 종료됩니다.".format(lastChar[-1]))
        return "do not think"

    comWord = engine.computerEg.useAgain(comWord,useData)
    if comWord == []:
        print("Word Chain Game Ending...")

    ### comWord  변수에 총 사용가능한 단어들이 모여있습니다. ###
    computerUse = engine.computerEg.selectWord(comWord)
    print("Moppy>", computerUse)
    useData.append(computerUse)
    lastChar = engine.defaultEg.getLastChar(computerUse)
    answer = computerUse

    return answer
