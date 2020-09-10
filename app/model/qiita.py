"""app/model/qiita.py
author          : nsuhara <na010210dv@gmail.com>
date created    : 2020/8/28
python version  : 3.7.3
"""
from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy.dialects import postgresql as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Qiita(Base):
    """Qiita
    """
    __tablename__ = 'qiita'

    id = Column(db.INTEGER, primary_key=True, autoincrement=True)
    date = Column(db.DATE, nullable=False)
    title = Column(db.VARCHAR(255), nullable=False)
    page_views_count = Column(db.INTEGER, nullable=False)
    likes_count = Column(db.INTEGER, nullable=False)
    url = Column(db.VARCHAR(255), nullable=False)
    created_at = Column(db.TIMESTAMP, nullable=False)

    def __init__(self, date, title, page_views_count, likes_count, url):
        self.date = date
        self.title = title
        self.page_views_count = page_views_count
        self.likes_count = likes_count
        self.url = url
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self):
        """to_dict
        """
        return {
            'id': self.id,
            'date': self.date,
            'title': self.title,
            'page_views_count': self.page_views_count,
            'likes_count': self.likes_count,
            'url': self.url,
            'created_at': self.created_at
        }
