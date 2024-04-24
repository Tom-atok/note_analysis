from typing import Tuple, List, Union, Optional, Dict
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import logging
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import MeCab

logging.basicConfig(level=logging.INFO)

def main(filename: str, n_components: int = 5, random_state: int = 42, stop_words: Optional[List[str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform topic analysis on the input data and identify the dominant topics.

    Parameters:
    - filename: The path to the pickle file containing the data.
    - n_components: The number of topics for the LDA model.
    - random_state: The random state for the LDA model.
    - stop_words: A list of stop words to be excluded during tokenization.

    Returns:
    - df: A pandas DataFrame containing the data with an additional column for the dominant topic.
    - topic_importance_df: A pandas DataFrame containing the topic importances.
    """
    try:
        # データの読み込みと前処理
        df, X, vectorizer = load_and_preprocess_data(filename, stop_words)

        # LDAモデルの構築
        lda = LatentDirichletAllocation(n_components=n_components, random_state=random_state)
        lda.fit(X)
        
        # トピックごとの単語の重要度を辞書形式にして保存する
        topic_importance_df = extract_topic_importance(lda=lda, vectorizer=vectorizer)

        # 各文書ごとのトピックの重要度をデータフレームに追加する
        doc_topic_dist = lda.transform(X)
        doc_topic_dist_df = pd.DataFrame(doc_topic_dist)
        df = pd.concat([df, doc_topic_dist_df], axis=1)

        return df, topic_importance_df

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, None



def load_and_preprocess_data(filename: str, stop_words: Optional[List[str]] = None) -> Tuple[pd.DataFrame, CountVectorizer]:
    """
    Load and preprocess the data.

    Parameters:
    - filename: The path to the pickle file containing the data.
    - stop_words: A list of stop words to be excluded during tokenization.

    Returns:
    - df: A pandas DataFrame containing the preprocessed data.
    - vectorizer: A CountVectorizer object fitted to the data.
    """
    # データの読み込み
    df = pd.read_csv(filename)

    # 本文がNoneとなっている行を削除
    df = df[df['body'].notnull()].reset_index(drop=True)
    # 全本文が公開されていない行を削除
    df = df[df['can_read'] == True].reset_index(drop=True)

    # 形態素分析の準備
    mecab = MeCab.Tagger("-Ochasen")

    # データフレームの各テキストをトークン化
    # データフレームの各テキストをトークン化
    df['tokenized_body'] = df['body'].apply(lambda x: tokenize(x, mecab, stop_words=stop_words))
    
    # CountVectorizerを使って文書-単語行列を作成
    vectorizer = CountVectorizer(tokenizer=lambda x: x.split())
    X = vectorizer.fit_transform(df['tokenized_body'].apply(' '.join))
    
    return df, X, vectorizer

def tokenize(text: str, mecab, stop_words: Optional[List[str]] = None) -> List[str]:
    """
    Tokenize the input text using MeCab.

    Parameters:
    - text: The input text to tokenize.
    - mecab: A MeCab Tagger object.
    - stop_words: A list of stop words to be excluded during tokenization.

    Returns:
    - words: A list of tokens extracted from the input text.
    """
    mecab.parse('')  
    node = mecab.parseToNode(text)
    words = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in ["名詞", "動詞", "形容詞"]:
            if (len(node.surface) > 1 or (len(node.surface) == 1 and node.feature.split(",")[1] in ["一般", "固有名詞"])) and (stop_words is None or node.surface not in stop_words):
                words.append(node.surface)
        node = node.next
    return words if words else ['']

def extract_topic_importance(lda, vectorizer) -> pd.DataFrame:
    """
    Extract the importance of different topics.

    Parameters:
    - lda: The LDA model.
    - vectorizer: The CountVectorizer object.

    Returns:
    - topic_importance_df: A pandas DataFrame containing the topic importances.
    """
    topic_importance = dict()
    for idx, topic in enumerate(lda.components_):
        topic_importance[f'Topic{idx}:'] = [(vectorizer.get_feature_names_out()[i], topic[i]) for i in topic.argsort()[:-10 - 1:-1]]
    
    topic_importance_df = pd.DataFrame(topic_importance)
    return topic_importance_df

def find_optimal_number_of_topics(filename: str, min_topics: int = 2, max_topics: int = 10, stop_words: Optional[List[str]] = None, save_fig: Optional[bool] = None) -> Tuple[int, List[float]]:
    """
    Find the optimal number of topics for LDA using perplexity.

    Parameters:
    - filename: The path to the pickle file containing the data.
    - min_topics: The minimum number of topics to consider.
    - max_topics: The maximum number of topics to consider.
    - stop_words: A list of stop words to be excluded during tokenization.

    Returns:
    - optimal_topics: The optimal number of topics.
    - perplexities: A list of perplexities for different numbers of topics.
    """
    try:
        logging.info('Starting to find the optimal number of topics...')
    
        # データの読み込みと前処理
        df, X, vectorizer = load_and_preprocess_data(filename, stop_words)

        logging.info('Data loaded successfully.')

        perplexities = []
        topic_range = range(min_topics, max_topics+1)
        
        for n_topics in topic_range:
            logging.info(f'Training LDA model with {n_topics} topics...')
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            lda.fit(X)
            perplexities.append(lda.perplexity(X))

        # Find the optimal number of topics
        optimal_topics = topic_range[perplexities.index(min(perplexities))]

        logging.info(f'The optimal number of topics is: {optimal_topics}')

        # Plotting
        plt.figure()
        plt.plot(topic_range, perplexities, marker='o')
        plt.title('Finding Optimal Number of Topics')
        plt.xlabel('Number of Topics')
        plt.ylabel('Perplexity')
        plt.grid(True)

        if save_fig == True:
            plt.savefig(f'finding_optimal_number_of_topics.png')
        
        plt.show()

        logging.info('Process completed successfully.')

        
        return optimal_topics, perplexities

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None, None
