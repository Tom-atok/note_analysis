import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from my_codes.database_setting import Engine
from my_codes.database_setting import Base

from my_codes.notes_database import Notes

########
# 前処理したデータから，データベースに新しいデータを追加する
########
# メイン関数
def add_csv_to_database(query):
    # データベースのセッションを作成
    Session = sessionmaker(bind=Engine)
    session = Session()

    # データベースから既存のキーを取得
    df_database = get_database_keys(session)

    # CSVファイルを読み込む
    df = read_csv_file(query)

    # 新しいデータをデータベースに挿入
    insert_new_data(df, df_database, Engine)

    session.close()

# サブ関数
def get_database_keys(session):
    # ORMを使って特定のカラムを取得
    database_keys = session.query(Notes.key).all()
    session.close()
    # リストをDataFrameに変換
    df_database = pd.DataFrame(database_keys, columns=['key'])
    return df_database

def read_csv_file(query):
    # CSV ファイルのパス
    csv_file_path = f'data/{query}/{query}_data_preprocessed.csv'
    # CSV ファイルの読み込み
    df = pd.read_csv(csv_file_path, index_col=0)
    return df

def insert_new_data(df, df_database, engine):
    # データベースに存在しないデータを取得
    new_df = df[~df['key'].isin(df_database['key'])]

    # 新しいデータをデータベースに挿入
    if not new_df.empty:
        new_df.to_sql('notes', con=engine, if_exists='append', index=False)
    else:
        print("新しいデータはありません。")

########
# query検索
########


