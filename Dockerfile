FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY . /app

RUN apt-get update
RUN apt-get -y install libsndfile1
RUN apt-get -y install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
RUN pip install -r /app/requirements.txt

EXPOSE 5000
ENV LISTEN_PORT 5000