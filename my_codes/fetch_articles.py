import requests
import time
import pandas as pd
import json
import os

#######
# 特定のクエリを含む記事を全取得
#######

from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# 単一のクエリに対して，指定した数の記事を取得
def fetch_articles(query, size=1, start=0, max_retries=3, backoff_factor=1):
    base_url = "https://note.com/api/v3/searches"
    params = {
        "context": "note",
        "q": query,
        "size": size,
        "start": start
    }

    retries = 0
    while True:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # HTTPエラーをチェック
            # 成功した場合はデータを返す
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return f"Failed to retrieve articles. HTTP Status code: {response.status_code}"
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return f"HTTP error occurred: {http_err}"
        except (ConnectionError, Timeout) as conn_err:
            print(f"Network error occurred: {conn_err}")
            retries += 1
            if retries >= max_retries:
                return f"Failed to retrieve articles after {max_retries} attempts."
            time.sleep(backoff_factor * (2 ** retries))  # Exponential backoff
        except RequestException as err:
            print(f"Error occurred: {err}")
            return f"Error occurred: {err}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return f"An unexpected error occurred: {e}"

# 複数のバッチを指定して，任意の数のデータを取得
def fetch_multiple_batches(query, size=1, batches=1, interval=1):
    '''バッチ数を指定して，任意の数のデータを取得する．取得できるデータがなくなったら終了．'''
    all_articles = []
    
    for i in range(batches):
        start = i * size
        response_data = fetch_articles(query, size=size, start=start)
        
        if isinstance(response_data, str):
            print(response_data)
            break

        notes_data = response_data.get('data', {}).get('notes', {})
        contents = notes_data.get('contents', [])
        all_articles.extend(contents)
        
        if not contents:  # 返されるコンテンツがない場合はループを抜ける
            break

        if i < batches - 1:
            print(f'{i+1}/{batches} has been fetched')
            time.sleep(interval)
    
    return all_articles

# データフレームに変換
def extract_data_to_dataframe(all_articles):
    # 各データ要素を抽出
    id_list = [item['id'] for item in all_articles]
    name_list = [item['name'] for item in all_articles]
    key_list = [item['key'] for item in all_articles]
    publish_at_list = [item['publish_at'] for item in all_articles]
    can_read = [item['can_read'] for item in all_articles]
    userid_list = [item['user']['id'] for item in all_articles]
    user_url_list = [item['user']['urlname'] for item in all_articles]
    username_list = [item['user']['name'] for item in all_articles]
    body_list = [item['body'] for item in all_articles]

    # データフレームに変換
    df = pd.DataFrame({
        'note_id': id_list,
        'name': name_list,
        'key':key_list,
        'publish_at': publish_at_list,
        'can_read': can_read,
        'user_id': userid_list,
        'urlname':user_url_list,
        'user_name':username_list,
        'body': body_list
    })

    return df

# クエリ検索では全文取得でいないため，クエリ検索取得したkeyから全文取得する
def fetch_articles_by_keys(data,interval=1):
    '''全文取得をするために，keyから読み込む'''
    keys = list(data['key'])
    all_articls = []
    counter = 0
    for key in keys:
        res = requests.get(f'https://note.com/api/v3/notes/{key}')
        data_json = json.loads(res.text) #JSON->Dict
        content = data_json['data'] #データ抽出

        all_articls.append(data_json['data']) #データ抽出
        
        time.sleep(interval)
        counter += 1
        if counter % 10 == 0:
            print(f'{counter}/{len(keys)} has fetched')
    print(f'fetching complete!')
    all_articls = pd.DataFrame(all_articls)
    all_articls.reset_index(drop=True, inplace=False) #indexを振り直す
    return all_articls


#######
# 特定のユーザーの全ポストを取得する
#######
def request_with_retry(url, max_retries=5):
    for _ in range(max_retries):
        try:
            response = requests.get(url, timeout=10)  # タイムアウトを10秒に設定
            response.raise_for_status()  # ステータスコードが200でない場合はエラーを発生させる
            return response
        except requests.RequestException as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(5)  # 5秒待ってから再試行
    raise Exception("Max retries reached. Exiting.")

def get_user_all_notes(username:str, maxpage:int=10000, interval:int=1.0):
    """ユーザーごとの全記事を取得する"""
    all_contents = []
    for numpage in range(1, maxpage+1):
        time.sleep(interval) # サーバー負荷軽減のため
        
        url = f'https://note.com/api/v2/creators/{username}/contents?kind=note&page={numpage}'
        res = request_with_retry(url)
        user_data_json = json.loads(res.text)  # JSON -> Dict
        
        if user_data_json['data']['contents']:  # データが空でない場合
            contents = user_data_json['data']['contents']  # キー抽出
            for content in contents:
                key = content['key']
                url = f'https://note.com/api/v3/notes/{key}'
                res = request_with_retry(url)
                data_json = json.loads(res.text)  # JSON -> Dict
                key_data = data_json['data']  # データ抽出
                all_contents.append(key_data)
            print(f'page {numpage} has fetched')
        else:
            print(f'page {numpage} is empty, finishing process!')
            return pd.DataFrame(all_contents)
    
    return pd.DataFrame(all_contents)

#######
# 特定のクエリを含む記事を投稿した全ユーザーの全ポストを取得する
#######

def save_checkpoint(user_df, counter, query):
    """中間結果を保存する関数"""
    checkpoint_path = f'data/{query}/checkpoint.csv'
    with open(checkpoint_path, 'w') as f:
        f.write(str(counter))
    user_df.to_csv(f'data/{query}/temp_fetched_user_all_post_raw_{str(counter)}.csv')
    print(f'CHECK POINT {counter} st user has fetched!')

def load_checkpoint(query):
    """中間結果と再開地点を読み込む関数"""
    checkpoint_path = f'data/{query}/checkpoint.csv'
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            counter = int(f.read().strip())
        user_df = pd.read_csv(f'data/{query}/temp_fetched_user_all_post_raw_{str(counter)}.csv', index_col=0)
        return user_df, counter
    return None, 0

def get_all_post_per_user(data, maxpage=10000, interval=1,query='temp',start_at=None):
    # 中間結果と再開地点を読み込む
    if start_at:
        user_df = None
        start_counter = start_at
    else:
        user_df, start_counter = load_checkpoint(query)
    
    # ユーザーURLの重複を削除する
    urlname_list = list(set(data['urlname'].tolist()))

    # 未処理のユーザーから再開
    for counter, user in enumerate(urlname_list[start_counter:], start=start_counter + 1):
        try:
            print(f'{counter}/{len(urlname_list)} st user start fetching')
            temp_df = get_user_all_notes(username=user, maxpage=maxpage, interval=interval)
            if user_df is None:
                user_df = temp_df
            else:
                user_df = pd.concat([user_df, temp_df], axis=0)
            
            # 中間結果を保存
            if counter % 10 == 0:
                save_checkpoint(user_df, counter,query)
                
        except Exception as e:
            print(f"Error fetching data for user {user}. Error: {e}")
    
    # 最後の結果も保存
    save_checkpoint(user_df, counter,query)
    
    print('Fetching has completed!')
    return user_df

def select_columns(user_df):
    select_columns = ['id','user_id','status','type','key','slug','name','body','created_at','can_read']
    usercolumns = ['key','urlname','nickname','note_count','created_at']

    selected_df = user_df[select_columns]
    selected_df = selected_df.reset_index(drop=True)

    user_info_dict = {key:[user_df['user'].iloc[row][key] for row in range(len(user_df))] for key in usercolumns}
    user_info_df = pd.DataFrame(user_info_dict)
    user_info_df = user_info_df.rename(columns={'key':'user_key','created_at':'user_created_at'})
    user_info_df = user_info_df.reset_index(drop=True)

    selected_df_adduserinfo = pd.concat([selected_df,user_info_df],axis=1)

    return selected_df_adduserinfo

#######
# クエリデータの操作に関わる
#######
def add_query_keys(df, query_key_path='data/query_key.csv'):
    """
    この関数は、与えられたDataFrameから 'key' 列を 'query_key.csv' という名前のCSVファイルに追加します。
    ファイルが既に存在する場合、'key' 列は既存のファイルに追加されます。
    
    パラメーター:
    - df: DataFrame - 'key' 列をCSVファイルに追加するためのDataFrame
    - query_key_path: str - 'key' 列を追加するCSVファイルのパス
    
    返り値: None
    """
    if not os.path.exists(query_key_path):
        df['key'].to_csv(query_key_path, index=False)
    else:
        with open(query_key_path, 'a') as f:
            df['key'].to_csv(f, header=False, index=False)
    
def load_query_keys(query_key_path='data/query_key.csv'):
    """
    この関数は、'query_key.csv' ファイルから 'key' 列を読み込み、それを返します。
    ファイルが存在しない場合、空のDataFrameが返されます。
    
    パラメーター:
    - query_key_path: str - 'key' 列を読み込むCSVファイルのパス

    返り値: DataFrame - 'key' 列を含むDataFrame
    """
    if os.path.exists(query_key_path):
        return pd.read_csv(query_key_path)
    else:
        return pd.DataFrame()


#######
# main関数
#######
def main(query, size=50, batches = 10000, interval=1, query_keys=None):
    
    directory = f'data/{query}'
    # 指定したディレクトリが存在するか確認します。
    if not os.path.exists(directory):
        # 存在しない場合、ディレクトリを作成します。
        os.makedirs(directory)

    # クエリを指定して，クエリに該当する記事を全件取得
    query_all = fetch_multiple_batches(query=query, size=size, batches=batches, interval=interval)
    print(f'fetching all articles by query has completed!')
    # 生データを保存
    with open(f'data/{query}/{query}_fetched_query_raw.json','w') as file:
        json.dump(query_all,file)
    print(f'all articles by query has saved')
    # データフレーム形式にする
    query_df = extract_data_to_dataframe(query_all)
    query_df.to_csv(f'data/{query}/{query}_fetchtd_df.csv')

    # query keysの読み込み
    loaded_query_keys = load_query_keys()
    print(f'query keys has loaded!')

    # query_dfからload_query_keysに含まれていないものを抽出
    query_df = query_df[~query_df['key'].isin(loaded_query_keys['key'])]
    print(f'query keys has extracted!')

    # queryごとの全文記事全件取得, デフォルトでは動かない
    if query_keys:
        query_keys_all = fetch_articles_by_keys(data=query_all,interval=interval)
        print(f'fetching all articles by keys has completed!')
        query_keys_all.to_csv(f'data/{query}/{query}_fetched_query_keys_all_raw.csv')
        print(f'all articles by keys has saved')

    # ユーザーごとの記事を取得する
    print(f'sart fetchnig all user post')
    all_user_data = get_all_post_per_user(data=query_df,interval=interval,query=query)
    print(f'fetching all user post has completed!')
    all_user_data.to_csv(f'data/{query}/{query}_fetched_user_all_post_raw.csv')
    print(f'all user post has saved')

    # 抽出
    selected_all_user_data = select_columns(all_user_data)
    selected_all_user_data.to_csv(f'data/{query}/{query}_user_all_post_df.csv')

    print(f'selected all user data has saved!')

    add_query_keys(selected_all_user_data)
    print(f'query keys has added!')
    
    # queryに合致するものを保存
    query_keys_all_df = selected_all_user_data[
        selected_all_user_data['id'].isin(list(query_df['note_id']))
        ]
    query_keys_all_df.to_csv(f'data/{query}/{query}_fetched_query_keys_all_df.csv')
    print(f'all articles mattched with query searched by keys has saved')

    return query_keys_all_df, selected_all_user_data