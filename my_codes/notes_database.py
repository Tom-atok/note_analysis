from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime

from my_codes.database_setting import Engine
from my_codes.database_setting import Base

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

if __name__ == "__main__":
    Base.metadata.create_all(Engine, checkfirst=True)

