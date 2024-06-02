from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# 接続先DBの設定
DATABASE = 'sqlite:///data/user_all_post.db'

# Engine の作成
Engine = create_engine(
  DATABASE,
  encoding="utf-8",
  echo=False
)
Base = declarative_base()

# Sessionの作成
session = Session(
  autocommit = False,
  autoflush = True,
  bind = Engine
)

# modelで使用する
Base = declarative_base()
Base.query = session.query_property()