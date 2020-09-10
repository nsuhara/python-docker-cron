"""app/main.py
author          : nsuhara <na010210dv@gmail.com>
date created    : 2020/8/28
python version  : 3.7.3
"""
import os
import sys
from datetime import datetime

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.qiita import Qiita


def get(url):
    """get
    """
    qiita_access_token = os.getenv('QIITA_ACCESS_TOKEN', '')
    if qiita_access_token == '':
        print('Error: please set \'QIITA_ACCESS_TOKEN\' to environment variable.')
        sys.exit()

    headers = {
        'Content-Type': 'application/json',
        'Charset': 'utf-8',
        'Authorization': 'Bearer {}'.format(qiita_access_token)
    }
    res = requests.get(url=url, headers=headers)
    print('{}, {}'.format(res.status_code, res.url))
    return res


def get_id_list():
    """get_list
    """
    res = get(url='https://{url}?page={page}&per_page={per_page}'.format(**{
        'url': os.getenv('QIITA_URL_LIST'),
        'page': os.getenv('QIITA_PAGE'),
        'per_page': os.getenv('QIITA_PER_PAGE')
    }))
    return [item.get('id') for item in res.json()]


def get_item(qiita_id):
    """get_item
    """
    res = get(url='https://{url}/{id}'.format(**{
        'url': os.getenv('QIITA_URL_ITEM'),
        'id': qiita_id
    }))
    item = res.json()
    return {
        'page_views_count': item.get('page_views_count'),
        'likes_count': item.get('likes_count'),
        'title': item.get('title'),
        'url': item.get('url')
    }


def output_db(items):
    """output_db
    """
    engine = create_engine(
        os.getenv('SQLALCHEMY_DATABASE_URI', ''),
        echo=bool(int(os.getenv('SQLALCHEMY_ECHO', '0'))),
        pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", '5')),
        max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", '10')),
        pool_timeout=int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", '30'))
    )
    create_session = sessionmaker(bind=engine)
    session = create_session()

    insert = list()
    date = datetime.now().date()

    session.query(Qiita).filter(Qiita.date == date).delete()

    for item in items:
        insert.append(Qiita(
            date=date,
            title=item.get('title'),
            page_views_count=item.get('page_views_count'),
            likes_count=item.get('likes_count'),
            url=item.get('url')
        ))

    session.add_all(insert)
    session.commit()


def output_log(items):
    """output_log
    """
    total_page_views_count = 0
    total_likes_count = 0

    print('-'*100)

    for item in items:
        total_page_views_count = total_page_views_count + \
            item.get('page_views_count')
        total_likes_count = total_likes_count+item.get('likes_count')

        print('page_views_count={}, likes_count={}, title={}, url={}'.format(
            str(item.get('page_views_count')).zfill(5),
            str(item.get('likes_count')).zfill(2),
            item.get('title'),
            item.get('url'))
        )

    print('\nitems_count={}, total_page_views_count={}, total_likes_count={}'.format(
        len(items), total_page_views_count, total_likes_count))

    print('-'*100)


def main():
    """main
    """
    items = list()

    for qiita_id in get_id_list():
        items.append(get_item(qiita_id=qiita_id))

    sorted_items = sorted(
        items, key=lambda x: x['page_views_count'], reverse=True)

    if os.getenv('OUTPUT', '') == 'output_db':
        output_db(items=sorted_items)
    else:
        output_log(items=sorted_items)


if __name__ == '__main__':
    main()
