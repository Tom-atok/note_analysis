import MeCab

def main(file_path,text,hit_word_list=True):
    jmfd = parse_dictionary_file(file_path)
    wakati_base_list = wakati_base_form(text)
    score =  calculate_score(wakati_base_list,jmfd['dictionary'])
    if hit_word_list:
        hit_word = search_words(wakati_base_list,jmfd['dictionary'])
        return score, hit_word
    return score

def parse_dictionary_file(file_path):
    '''dictionary.txtから判例と辞書を，辞書形式で取り出すための関数'''
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    examples = {}
    dictionary = {}

    for line in lines:
        if line.strip() == '%':
            continue

        parts = line.strip().split('\t')
        if len(parts) == 2:
            key, value = parts
            examples[key] = value
        elif len(parts) > 2:
            word = parts[0]
            values = [int(x) for x in parts[1:] if x]
            sparse_values = [1 if i in values else 0 for i in range(1, 12)]
            dictionary[word] = sparse_values
    return {'examples': examples, 'dictionary': dictionary}


def wakati(text):
    '''分かち書きを行うための関数'''
    mecab = MeCab.Tagger("-Owakati")
    wakati_text = mecab.parse(text).strip()
    return wakati_text

def wakati_base_form(text):
    '''分かち書きを行い，原型で表示'''
    mecab = MeCab.Tagger()
    node = mecab.parseToNode(text)
    base_form_words = []

    while node:
        feature = node.feature.split(",")
        base_form = feature[6]
        if base_form != "*":
            base_form_words.append(base_form)
        else:
            base_form_words.append(node.surface)
        node = node.next

    wakati_base_form_text = " ".join(base_form_words).strip()
    return wakati_base_form_text.split(' ')

def calculate_score(lst, dic):
    '''分かち書きされたリストと辞書を用いて，スコアを出す．'''
    score = [0] * 11  # スコアを初期化
    
    for word in lst:
        for key in dic.keys():
            if key.endswith('*') and word.startswith(key[:-1]):  # '*'が付いた単語に対しては、前方一致をチェックする
                score = [score[i] + dic[key][i] for i in range(11)]
            elif word == key:
                score = [score[i] + dic[key][i] for i in range(11)]
    
    return score

def search_words(lst, dic):
    '''どの単語がヒットしたのかを検索する'''
    result = {}
    
    for word in lst:
        for key in dic.keys():
            if key.endswith('*') and word.startswith(key[:-1]):  # '*'が付いた単語に対しては、前方一致をチェックする
                if key in result:
                    result[key][1] += 1
                else:
                    result[key] = [dic[key], 1]
            elif word == key:
                if key in result:
                    result[key][1] += 1
                else:
                    result[key] = [dic[key], 1]
    
    return result


