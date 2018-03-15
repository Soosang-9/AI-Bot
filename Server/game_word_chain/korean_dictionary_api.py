import requests
import os
import xml.etree.ElementTree as ET

def posCheck(korean):
    kda_key = os.getenv('dictionary_key')
    q = korean
    url = "https://opendict.korean.go.kr/api/search" \
          "?key={}" \
          "&q={}".format(kda_key, q)

    postXML = requests.post(url=url)
    data = postXML.text
    # print(data)

    f = open("game_word_chain/data.xml", 'w')
    f.write(data)
    f.close()

    file_name = "game_word_chain/data.xml"
    doc = ET.parse(file_name)
    root = doc.getroot()

    wordList = []
    posList = []

    for item in root.iter("item"):
        word = item.findtext("word")
        wordList.append(word)

    for sense in root.iter("sense"):
        pos = sense.findtext("pos")
        posList.append(pos)

    print("word:", wordList[0], "pos:", posList[0])

    if posList[0] == '명사':
        check = 'true'
    else:
        check = 'false'

    return check
