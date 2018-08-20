FROM python:3.6.6

RUN apt-get update && apt-get install -y libmariadbclient-dev
RUN pip install --upgrade pip

RUN mkdir /progimage

WORKDIR /progimage

ADD . /progimage/

RUN pip install -r requirements.txt

