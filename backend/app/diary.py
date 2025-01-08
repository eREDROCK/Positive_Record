import csv
import MeCab
import ipadic
import os

# MeCab Taggerオブジェクトを作成
mecab = MeCab.Tagger(ipadic.MECAB_ARGS)

pth = os.path.dirname(__file__)
# MeCabの動詞情報取得
csv_file = open(pth + "/yougen/Verb.csv", "r", encoding='shift-jis')
#リスト形式
verb_features = csv.reader(csv_file)

# MeCabの形容詞情報取得
csv_file = open(pth + "/yougen/Adj.csv", "r", encoding='shift-jis')
#リスト形式
adj_features = csv.reader(csv_file)

verb_list = []
adj_list = []


class Morpheme:
    def __init__(self, node):
        features = node.feature.split(",")
        self.hinshi = features[0]
        self.surface = node.surface
        if len(features) > 6 and features[6] != "*" : 
            self.genkei = features[6]
        else:
            self.genkei = self.surface


class Verb:
    def __init__(self, features):
        self.genkei = features[10]
        self.katuyou_gobi = features[8]
        self.katuyoukei = {features[9] : features[0]}
    
    def add_katuyoukei(self, features):
        self.katuyoukei[features[9]] = features[0]
    
    def pastTense(self):
        if '連用タ接続' in self.katuyoukei :
            pastVerb = self.katuyoukei['連用タ接続']
            if pastVerb[-1] == 'ん' :
                return pastVerb + "だ"
            else : 
                return pastVerb + "た"
        elif '連用形' in self.katuyoukei:
            return self.katuyoukei['連用形'] + "た"
        elif '未然形' in self.katuyoukei:
            return self.katuyoukei['未然形'] + "た"
        return self.genkei
    def search_katuyoukei(self, word):
        if word in self.katuyoukei.values():
            return True
        return False

class Adj:
    def __init__(self, features):
        self.genkei = features[10]
        self.katuyou_gobi = features[8]
        self.katuyoukei = {features[9] : features[0]}
    
    def add_katuyoukei(self, features):
        self.katuyoukei[features[9]] = features[0]
    
    def pastTense(self):
        if '連用タ接続' in self.katuyoukei :
            pastVerb = self.katuyoukei['連用タ接続']
            if pastVerb[-1] == 'ん' :
                return pastVerb + "だ"
            else : 
                return pastVerb + "た"
        elif '連用形' in self.katuyoukei:
            return self.katuyoukei['連用形'] + "た"
        elif '未然形' in self.katuyoukei:
            return self.katuyoukei['未然形'] + "た"
        return self.genkei
    def search_katuyoukei(self, word):
        if word in self.katuyoukei.values():
            return True
        return False

def init_verbs(verb_list):
    genkei = ""
    for row in verb_features:
        if genkei == row[10]:
            verb_list[-1].add_katuyoukei(row)
            continue
        genkei = row[10]
        verb_list.append(Verb(row))
    return;

def init_adjs(adj_list):
    genkei = ""
    for row in adj_features:
        if genkei == row[10]:
            adj_list[-1].add_katuyoukei(row)
            continue
        genkei = row[10]
        adj_list.append(Adj(row))
    return;

def change_past(morpheme):
    for verb in verb_list:
        if verb.genkei == morpheme.genkei and verb.search_katuyoukei(morpheme.surface):
            return verb.pastTense()
    for adj in adj_list:
        if adj.genkei == morpheme.genkei and adj.search_katuyoukei(morpheme.surface):
            return adj.pastTense()
    return morpheme.genkei

# 初期化
init_verbs(verb_list)
init_adjs(adj_list)
csv_file.close()

def split_sentence(input):
    sentences = []
    for moji in input:
        if moji == "." or moji == "。" or moji == "．":
            sentences.append(input.split(moji,1)[0])
            sentences.extend(split_sentence(input.split(moji,1)[1]))
            break
    if len(sentences) == 0 and len(input) > 2:
        sentences.append(input)
    return sentences

def generate_diary(messages):
    user_diary = ""
    diary_sentences = []
    morpheme_list = []
    user_inputs = []
    sentences = []
    diary_sentence = ""
    for message in messages:
        if message.role == "User":
            user_inputs.append(message.text)
    for user_input in user_inputs:
        sentences.clear()
        sentences = split_sentence(user_input)
        for sentence in sentences : 
            morpheme_list.clear()
            diary_sentence = ""
            node = mecab.parseToNode(sentence)
            while node:
                morpheme_list.append(Morpheme(node))
                node = node.next
            finish_index = len(morpheme_list)
            for i in range(len(morpheme_list) - 1, 0 ,-1):
                if morpheme_list[i].hinshi == "動詞" or morpheme_list[i].hinshi == "形容詞":
                    morpheme_list[i].surface = change_past(morpheme_list[i])
                    finish_index = i + 1
                    break
            for k in range(1,finish_index):
                diary_sentence += morpheme_list[k].surface
            diary_sentences.append(diary_sentence + "。")
            user_diary += diary_sentence + "。"

    print(user_diary)
    return user_diary
