# Docker Compose + Daemon(cron)でPython Scriptを定期実行する

## はじめに

`Mac環境の記事ですが、Windows環境も同じ手順になります。環境依存の部分は読み替えてお試しください。`

### 目的

Docker ComposeでDaemon(cron)とDatabase(PostgreSQL)を立ち上げて、Python Scriptを定期に実行します。

この記事を最後まで読むと、次のことができるようになります。

| No.  | 概要           | キーワード     |
| :--- | :------------- | :------------- |
| 1    | Docker Compose | docker-compose |
| 2    | cron           | crond          |
| 3    | SQLAlchemy     | sqlalchemy     |
| 4    | PostgreSQL     | psycopg2       |
| 5    | Alembic        | alembic        |

### 実行環境

| 環境            | Ver.     |
| :-------------- | :------- |
| macOS Catalina  | 10.15.6  |
| Docker          | 19.03.12 |
| Python          | 3.7.3    |
| PostgreSQL      | 11.5     |
| alembic         | 1.4.2    |
| psycopg2-binary | 2.8.6    |
| requests        | 2.24.0   |
| SQLAlchemy      | 1.3.19   |

### ソースコード

実際に実装内容やソースコードを追いながら読むとより理解が深まるかと思います。是非ご活用ください。

[GitHub](https://github.com/nsuhara/python-docker-cron.git)

### 関連する記事

- [Docker Compose](https://docs.docker.com/compose/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Heroku SchedulerでPythonを定期実行する](https://qiita.com/nsuhara/items/fac20adb6b0a122a3709)

## システム構成

### シナリオ

日々のQiitaアクセス累計数を保存する。

1. Docker ComposeでDaemon(cron)とDatabase(PostgreSQL)を立ち上げる
2. Daemon(cron)の起動時刻を23:00に設定する
3. Daemon(cron)の起動をトリガーにPython Scriptを実行する
4. Python ScriptでQiita情報を取得してPostgreSQLへ登録する

### 実行結果

Docker

```docker.sh
qiita=# SELECT * from qiita ORDER BY date DESC, page_views_count DESC;
 id |    date    |                                   title                                   | page_views_count | likes_count |                         url                          |         created_at
----+------------+---------------------------------------------------------------------------+------------------+-------------+------------------------------------------------------+----------------------------
  1 | 2020-09-10 | REST APIを使ってSalesforceのデータを取得する                              |            11571 |          23 | https://qiita.com/nsuhara/items/19cf8ec89b88fb3deb39 | 2020-09-10 12:48:23.512842
  2 | 2020-09-10 | AlexaスキルをPython/Lambdaで実装する                                      |             4888 |          11 | https://qiita.com/nsuhara/items/5b19cfb5ffb897bd4cfd | 2020-09-10 12:48:23.513017
  3 | 2020-09-10 | Salesforceの添付ファイルに制限をかける                                    |             4611 |           6 | https://qiita.com/nsuhara/items/bd41c9ad946b8b832207 | 2020-09-10 12:48:23.51307
  4 | 2020-09-10 | Swift向け単体テスト(Unit Test)の作り方                                    |             4214 |          12 | https://qiita.com/nsuhara/items/bc06c07ff30a5b78696d | 2020-09-10 12:48:23.51313
  5 | 2020-09-10 | Kony AppPlatformを使ってiOS/Androidアプリを作成する                       |             3612 |           3 | https://qiita.com/nsuhara/items/c28d838492512850520c | 2020-09-10 12:48:23.513182
  6 | 2020-09-10 | Flask-SQLAlchemy + PostgreSQLでWebサービスを作成する                      |             2842 |           7 | https://qiita.com/nsuhara/items/fa5998c0b2f4fcefbed4 | 2020-09-10 12:48:23.513237
  7 | 2020-09-10 | Heroku + Selenium + ChromeでWEBプロセスを自動化する                       |             2719 |          15 | https://qiita.com/nsuhara/items/76ae132734b7e2b352dd | 2020-09-10 12:48:23.513292
  8 | 2020-09-10 | Docker + FlaskでWebサービスを作成する                                     |             2368 |           7 | https://qiita.com/nsuhara/items/c7eff7fae3801f85b5cd | 2020-09-10 12:48:23.513343
  9 | 2020-09-10 | Heroku SchedulerでPythonを定期実行する                                    |             2232 |           4 | https://qiita.com/nsuhara/items/fac20adb6b0a122a3709 | 2020-09-10 12:48:23.513393
 10 | 2020-09-10 | Messaging API + LIFF + Heroku + Flask + Framework拡張でLINE BOTを作成する |             1913 |           8 | https://qiita.com/nsuhara/items/0c431913165e4af0f8f5 | 2020-09-10 12:48:23.513449
 11 | 2020-09-10 | SalesforceのLightningデータサービス(LDS)について学ぶ                      |             1636 |           4 | https://qiita.com/nsuhara/items/ecd77def7aa1f985efcc | 2020-09-10 12:48:23.513503
 12 | 2020-09-10 | FlaskでRESTful Webサービスを作成する                                      |             1571 |           5 | https://qiita.com/nsuhara/items/449835bc94f0fb3bbcbd | 2020-09-10 12:48:23.513553
 13 | 2020-09-10 | AWS-Lambda + PythonでCSVデータをAWS-S3に書き込む                          |             1565 |           2 | https://qiita.com/nsuhara/items/b2bd1d2623bca0f767f8 | 2020-09-10 12:48:23.513604
 14 | 2020-09-10 | Kony AppPlatformで作成したiOS/Androidアプリのコーディングについて学ぶ     |             1536 |           1 | https://qiita.com/nsuhara/items/bf0e8884a7efc3c55176 | 2020-09-10 12:48:23.513654
 15 | 2020-09-10 | Pythonを使ってJSONからWord(docx)を作成する                                |             1511 |           2 | https://qiita.com/nsuhara/items/3ba2fa7db38acd04f448 | 2020-09-10 12:48:23.513708
 16 | 2020-09-10 | AWS-Lambda + PythonでAWS-RDS/PostgreSQLのテーブルを読み込む               |             1408 |           3 | https://qiita.com/nsuhara/items/dd780c2622258d10f961 | 2020-09-10 12:48:23.51376
 17 | 2020-09-10 | AWS-Lambda + Python + CronでWEBスクレイピングを定期的に実行する           |             1342 |           5 | https://qiita.com/nsuhara/items/0d36600511fc162827f6 | 2020-09-10 12:48:23.513819
 18 | 2020-09-10 | Django + SQLAlchemy + SQLite3 / PostgreSQLでWebアプリを作成する           |             1287 |           3 | https://qiita.com/nsuhara/items/4ab5366273082ee0aa73 | 2020-09-10 12:48:23.513874
 19 | 2020-09-10 | Kony AppPlatformで作成したiOS/AndroidアプリとSalesforceをデータ連携する   |             1088 |           1 | https://qiita.com/nsuhara/items/756120f1bddc6f8fe78b | 2020-09-10 12:48:23.513928
 20 | 2020-09-10 | Kony AppPlatformで作成したiOS/AndroidアプリのAuto Layoutについて学ぶ      |              898 |           0 | https://qiita.com/nsuhara/items/a52abd9861c51823ecec | 2020-09-10 12:48:23.513984
 21 | 2020-09-10 | PythonでAWS-S3の署名付き(期限付き)URLを生成する                           |              723 |           2 | https://qiita.com/nsuhara/items/20160b080c2b30d57729 | 2020-09-10 12:48:23.514131
 22 | 2020-09-10 | Kong API GatewayのGUI/Kongaを構築する                                     |              665 |           3 | https://qiita.com/nsuhara/items/a0de75e6767f98cc8fec | 2020-09-10 12:48:23.51419
 23 | 2020-09-10 | Raspberry PiとPythonでリモコンカーを作成する                              |              637 |           2 | https://qiita.com/nsuhara/items/7970b5dfe95ea76c93d6 | 2020-09-10 12:48:23.514248
 24 | 2020-09-10 | Kong API Gatewayを構築する                                                |              535 |           1 | https://qiita.com/nsuhara/items/ad1d8fa1faad7940b5c1 | 2020-09-10 12:48:23.514297
 25 | 2020-09-10 | Raspberry PiのセットアップからPython環境のインストールまで                |              529 |           0 | https://qiita.com/nsuhara/items/05a2b41d94ced1f54316 | 2020-09-10 12:48:23.514365
 26 | 2020-09-10 | Raspberry PiとPythonでLCD(16x2)ゲームを作成する                           |              424 |           0 | https://qiita.com/nsuhara/items/57105fd232feffbcd05c | 2020-09-10 12:48:23.514416
 27 | 2020-09-10 | Raspberry PiとOpenCVでWEB監視カメラを作成する                             |              392 |           0 | https://qiita.com/nsuhara/items/37fcbc9d0e8209080032 | 2020-09-10 12:48:23.514466
 28 | 2020-09-10 | Flask-SQLAlchemyでUPSERTを実装する方法                                    |              389 |           0 | https://qiita.com/nsuhara/items/86570f789093222252b1 | 2020-09-10 12:48:23.514518
 29 | 2020-09-10 | Qiita API + Pythonで記事のアクセス数やいいね数を取得する                  |              332 |           0 | https://qiita.com/nsuhara/items/b27b84f0150c3f6534ec | 2020-09-10 12:48:23.514569
 30 | 2020-09-10 | CSVデータをPostgreSQLに一括挿入する方法                                   |              145 |           0 | https://qiita.com/nsuhara/items/a1b75e0557ed134c5302 | 2020-09-10 12:48:23.514635
(30 rows)
```

Heroku

<img width="800" alt="2020-09-10.png" src="https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/326996/ee0f124e-c35e-9f1d-d66c-0ae8503755bf.png">

### アプリ構成

```tree.sh
/
├── Dockerfiles
│   ├── app
│   │   ├── Dockerfile
│   │   ├── crontab
│   │   ├── docker-compose.yml
│   │   ├── entrypoint.sh
│   │   └── qiita.sh
│   └── docker_compose_up.sh
└── app
     ├── __init__.py
     ├── alembic.ini
     ├── config
     │   └── qiita_access_token
     ├── main.py
     ├── migration
     │   ├── README
     │   ├── env.py
     │   ├── script.py.mako
     │   └── versions
     │       └── 62fb1bcf0a8a_create_table.py
     ├── model
     │   ├── __init__.py
     │   └── qiita.py
     └── requirements.txt
```

## Hands-on

### ダウンロード

```command.sh
~% git clone https://github.com/nsuhara/python-docker-cron.git -b master
```

### サービス起動

```command.sh
~% cd python-docker-cron/
~% sh Dockerfiles/docker_compose_up.sh
```

### サービス終了

```command.sh
~% Control Key + C
```

## Python Script

```tree.sh
/
└── app
     ├── main.py
     └── model
          ├── __init__.py
          └── qiita.py
```

### Model作成

```qiita.py
"""app/model/qiita.py
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
```

### Main作成

```main.py
"""app/main.py
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
```

### Qiitaアクセストークン設定

```command.sh
~% echo "export QIITA_ACCESS_TOKEN={qiita access token}" > app/config/qiita_access_token
```

- メモ: [アクセストークン](https://qiita.com/nsuhara/items/b27b84f0150c3f6534ec#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3)

## Database Migration

```tree.sh
/
└── app
     ├── alembic.ini
     └── migration
          ├── README
          ├── env.py
          ├── script.py.mako
          └── versions
              └── 62fb1bcf0a8a_create_table.py
```

### Alembicインストール

```command.sh
~% pip install alembic
```

### Alembic初期化

```command.sh
~% alembic init {directory}
```

### Alembic設定

```command.sh
~% vim app/alembic.ini
```

```command.sh
- sqlalchemy.url = driver://user:pass@localhost/dbname
+ sqlalchemy.url = postgresql+psycopg2://postgres:postgres@docker_db:5432/qiita
```

### スクリプト作成

```command.sh
~% alembic revision -m 'Create Table'
```

- メモ: `app/migration/versions/{revision id}_create_table.py`が生成される

### スクリプト編集

```create_table.py
"""Create Table
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as db

# revision identifiers, used by Alembic.
revision = '62fb1bcf0a8a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'qiita',
        sa.Column('id', db.INTEGER, primary_key=True),
        sa.Column('date', db.DATE, nullable=False),
        sa.Column('title', db.VARCHAR(255), nullable=False),
        sa.Column('page_views_count', db.INTEGER, nullable=False),
        sa.Column('likes_count', db.INTEGER, nullable=False),
        sa.Column('url', db.VARCHAR(255), nullable=False),
        sa.Column('created_at', db.TIMESTAMP, nullable=False),
    )


def downgrade():
    pass
```

### テーブル手動生成

```command.sh
~% python app/migration/versions/{revision id}_create_table.py
```

## Docker Compose

```tree.sh
/
├── Dockerfiles
│   ├── app
│   │   ├── Dockerfile
│   │   ├── crontab
│   │   ├── docker-compose.yml
│   │   ├── entrypoint.sh
│   │   └── qiita.sh
│   └── docker_compose_up.sh
└── app
```

### docker_compose_up.sh

```docker_compose_up.sh
#!/bin/sh

docker stop $(docker ps -q)
docker rm $(docker ps -q -a)
# docker rmi $(docker images -q) -f

rsync -av --exclude=app/tests* app Dockerfiles/app
docker-compose -f Dockerfiles/app/docker-compose.yml up --build
```

### docker-compose.yml

```docker-compose.yml
version: '3'
services:
  docker_db:
    image: postgres:11.5
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'qiita'
      POSTGRES_INITDB_ARGS: '--encoding=UTF-8'

  app:
    build: .
    depends_on:
      - docker_db
    volumes:
      - ./crontab:/var/spool/cron/crontabs/root
    environment:
      PYTHONPATH: '/code/'
      TZ: 'Asia/Tokyo'
      QIITA_PAGE: '1'
      QIITA_PER_PAGE: '100'
      QIITA_URL_ITEM: 'qiita.com/api/v2/items'
      QIITA_URL_LIST: 'qiita.com/api/v2/authenticated_user/items'
      OUTPUT: 'output_db'
      SQLALCHEMY_DATABASE_URI: 'postgresql+psycopg2://postgres:postgres@docker_db:5432/qiita'
      SQLALCHEMY_ECHO: '1'
      SQLALCHEMY_POOL_SIZE: '5'
      SQLALCHEMY_MAX_OVERFLOW: '10'
      SQLALCHEMY_POOL_TIMEOUT: '30'
```

### Dockerfile

```Dockerfile
FROM python:3.7

RUN mkdir /code
WORKDIR /code

ADD entrypoint.sh /code/entrypoint.sh
ADD qiita.sh /code/qiita.sh
ADD app/ /code

RUN export -p
RUN chmod +x /code/entrypoint.sh
RUN chmod +x /code/qiita.sh

RUN apt-get update && apt-get -y install busybox-static

RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

RUN touch /var/log/cron.log

# EXPOSE 0000

CMD ["/code/entrypoint.sh"]
```

### entrypoint.sh

```entrypoint.sh
#!/bin/bash

sleep 5
# set qiita access token to environment variable
source /code/config/qiita_access_token
# migrate database
alembic upgrade head
# run script at 23:00, 0 23 * * * /code/qiita.sh  >> /var/log/cron.log 2>&1
busybox crond -l 8 -L /dev/stderr -f
```

### crontab

```crontab
0 23 * * * /code/qiita.sh  >> /var/log/cron.log 2>&1
```

### qiita.sh

```qiita.sh
#!/bin/sh

python /code/main.py
```

### 各種サービス起動

```command.sh
~% sh Dockerfiles/docker_compose_up.sh
```

### ローカルからDockerコンテナへログイン

```command.sh
docker ps
# CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
# 0af68012c7c9        app_app             "/code/entrypoint.sh"    38 seconds ago      Up 37 seconds       0.0.0.0:8000->8000/tcp   app_app_1
# 9901a105e8d5        postgres:11.5       "docker-entrypoint.s…"   39 seconds ago      Up 37 seconds       0.0.0.0:5432->5432/tcp   app_postgres_1

docker exec -i -t {CONTAINER ID} /bin/bash
```

### ローカルからDocker-PostgreSQLへログイン

```command.sh
~% psql -h localhost -p 5432 -d qiita -U postgres
```

## おまけ:Heroku

### runtime.txt作成

[Supported runtimes](https://devcenter.heroku.com/articles/python-support#supported-runtimes)

```command.sh
~% cd python-docker-cron/
~% echo python-3.7.9 > app/runtime.txt
```

### Heroku Postgres登録

1. {app-name} > `Resources`タブ > Add-onsの検索で`Heroku Postgres`を入力して選択 > `Provision`ボタン

### 環境変数設定

1. {app-name} > `Settings`タブ > `Reveal Config Vars`ボタン > 環境変数を登録

- メモ1: [/config/output_db](./config/output_db)
- メモ2: [アクセストークン](https://qiita.com/nsuhara/items/b27b84f0150c3f6534ec#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3)
- メモ3: `SQLALCHEMY_DATABASE_URI`は`Heroku Postgres`に合わせること
- メモ4: `QIITA_ACCESS_TOKEN`の登録を忘れないこと

### alembic.ini編集

```command.sh
~% cd python-docker-cron/
~% vim app/alembic.ini
```

```command.sh
- sqlalchemy.url = postgresql+psycopg2://postgres:postgres@docker_db:5432/qiita
+ sqlalchemy.url = {SQLALCHEMY_DATABASE_URIと同じURL}
```

### デプロイ

```command.sh
~% cd python-docker-cron/app/
~% git init
~% git commit -am "make it better"
~% heroku login
~% heroku git:remote -a {app-name}
~% git push heroku master
```

### Heroku Postgres Migration

```command.sh
~% cd python-docker-cron/
~% heroku run python migration/versions/62fb1bcf0a8a_create_table.py
```

or

```command.sh
~% heroku pg:psql {database} --app {app-name}
```

```command.sh
{app-name}::DATABASE=> CREATE TABLE qiita (
    id SERIAL NOT NULL,
    date date not null,
    title VARCHAR(255) NOT NULL,
    page_views_count Integer NOT NULL,
    likes_count Integer NOT NULL,
    url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
);
```

### Heroku Scheduler登録

1. {app-name} > Resourcesタブ > Add-onsの検索で`Heroku Scheduler`を入力して選択 > `Provision`ボタン
2. Heroku Scheduler > `Add Job`ボタン
3. `Schedule`に実行周期を設定
4. `Run Command`に`python main.py`を設定

- メモ1: [Heroku SchedulerでPythonを定期実行する](https://qiita.com/nsuhara/items/fac20adb6b0a122a3709)
- メモ2: クレジットカードの登録が必要
