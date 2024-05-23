import pandas as pd
from bs4 import BeautifulSoup
import pickle
import re
import numpy as np
import MeCab

def main(query, data_dict_path='data'):
    # データを読み込む
    data = read_data(query, data_dict_path)

    # ユーザーネームをpickle形式で保存する
    urlname = data['urlname'].unique()
    with open(f'data/{query}/{query}_urlname_list.pickle','wb') as f:
        pickle.dump(list(set(urlname)),f)
    
    # 行削除
    data = remove_nan(data)

    # テキストデータをクリーニングする
    data['body'] = data['body'].apply(clean_text)

    # MeCabのインスタンスを作成
    mecab = MeCab.Tagger()
    
    # データフレームの各テキストをトークン化
    data['tokenized_body'] = data['body'].apply(lambda x: tokenize(x, mecab))

    data = data.reset_index(drop = True)

    # トークン化したデータを保存
    data.to_csv(f'{data_dict_path}/{query}_data_preprocessed.csv')

    return data




########
# 関数
########

def read_data(query, data_dict_path='data'):
    '''データを読み込む，queryは検索語，data_dict_pathはデータが保存されているディレクトリのパス'''
    data_path = f'{data_dict_path}/{query}/{query}_user_all_post_df.csv'
    data = pd.read_csv(data_path,index_col=0)
    return data

def remove_nan(data):
    '''dataのtext列にNaNがある行を削除する'''
    # 本文がNoneとなっている行を削除
    data = data[data['body'].notnull()].reset_index(drop=True)
    # 全本文が公開されていない行を削除
    data = data[data['can_read'] == True].reset_index(drop=True)
    return data

def clean_text(text):
    '''テキストをクリーニングする関数'''
    # もしtextがNaN（浮動小数点数）なら、空の文字列に置き換える
    if pd.isna(text):
        text = ''
    else:
        # もし既に文字列でない場合は、文字列に変換する
        text = str(text)
    
    # BeautifulSoupを使ってHTMLタグを削除する
    text = BeautifulSoup(text, "html.parser").get_text()
    # 正規表現を使ってURLを削除する
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)  # wwwで始まるURLを削除する
    # エスケープ文字を削除する
    text = re.sub(r'[\t\n\r\f\v]', ' ', text)  # スペースに置換する
    text = re.sub(r'&[\w#]+;', ' ', text)  # HTMLエンティティをスペースに置換する
    # 余分なスペースやタブなどを削除する
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text, mecab, stop_words= None):
    '''テキストを形態素解析して、名詞、動詞、形容詞、副詞、形容動詞の単語のリストを返す関数, 
    textはテキストデータ，mecabはMeCabのインスタンス，stop_wordsは除外する単語のリスト'''
    mecab.parse('')  
    node = mecab.parseToNode(text)
    words = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in ["名詞", "動詞", "形容詞",'副詞','形容動詞']:
            if (len(node.surface) > 1 or (len(node.surface) == 1 and node.feature.split(",")[1] in ["一般", "固有名詞"])) and (stop_words is None or node.surface not in stop_words):
                words.append(node.surface)
        node = node.next
    return words if words else ['']