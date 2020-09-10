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
