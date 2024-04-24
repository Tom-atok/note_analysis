# データを読み込む
import pandas as pd
import logging

# ロギングの基本設定。デフォルトではWARNING以上のログが出力される
logging.basicConfig(level=logging.INFO)
# ファイルを読み込む


def main(query,n_topics,n_moral_clusters,n_samples=50):
    data = pd.read_pickle(f'data/{query}/{query}_data_preprocessed.pickle')
    extract_bodies_on_topics(data=data,n_topics=n_topics,n_samples=n_samples)
    extract_bodies_on_moral_cluster(data=data,n_moral_clusters=n_moral_clusters,n_samples=n_samples)

def extract_bodies_on_topics(query==None,data,n_topics,n_samples=50):
    if query == True:
        data = pd.read_pickle(f'data/{query}/{query}_data_preprocessed.pickle')
    #トピックのデータを読み込む
    keys = pd.read_csv(f'data/{query}/{query}_TopicAnalysis_{n_topics}topics_df.csv',index_col=0)
    #文書のキーから文書を取り出す
    for i in range(n_topics):
        dat = keys.sort_values(by=f'Topic_{str(i)}',ascending=False).iloc[:n_samples]
        body = data[data.key.isin(dat['key'])][['urlname','key','body']]
        body[f'Topic_{str(i)}'] = dat[f'Topic_{str(i)}']
        body.to_csv(f'data/{query}/{query}_bodys_{n_topics}Topics_Topic{str(i)}.csv')
        logging.info(f'topic{i} has completed')
    
def extract_bodies_on_moral_cluster(query==None,data,n_moral_clusters,n_samples=50):
    if query == True:
        data = pd.read_pickle(f'data/{query}/{query}_data_preprocessed.pickle')
    else:
        data = data
    #特定のモラルクラスターに属する記事を読み込む
    keys = pd.read_csv(f'data/{query}/{query}_data_MoralClusterIntegrated_{n_moral_clusters}clusters.csv')
    doc_keys_dic = dict()
    #特定のモラルクラスターに属するユーザーのurlnameの辞書を作成する
    for mc in range(n_moral_clusters):
        mc_name = f'mc{str(mc)}'
        doc_keys_dic[mc_name] = keys[keys.moral_cluster == mc][['urlname','moral_cluster']]
    #mc_urlnameの辞書を参照し，bodyを抽出する
    for mc in range(n_moral_clusters):
        mc_name = f'mc{mc}'
        body = data[data.urlname.isin(doc_keys_dic[mc_name].urlname)][['urlname','key','body']].sample(n_samples)
        body.to_csv(f'data/{query}/{query}_bodys_{str(n_moral_clusters)}MC_mc{str(mc)}.csv')
        logging.info(f'topic{mc} has completed')