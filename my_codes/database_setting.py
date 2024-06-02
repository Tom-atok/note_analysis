from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースエンジンの作成（例：SQLite）
engine = create_engine('sqlite:///user_all_post.db', echo=True)

# Base クラスの作成
Base = declarative_base()

# Notes クラスの定義
class Notes(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer)
    user_id = Column(Integer)
    status = Column(Text)
    type = Column(Text)
    key = Column(String, primary_key=True, unique=True)
    slug = Column(Text)
    name = Column(Text)
    body = Column(Text)
    created_at = Column(DateTime)
    can_read = Column(Boolean)
    user_key = Column(Text)
    urlname = Column(Text)
    nickname = Column(Text)
    note_count = Column(Integer)
    user_created_at = Column(DateTime)
    tokenized_body = Column(Text)

# テーブルの作成
Base.metadata.create_all(engine)

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()
