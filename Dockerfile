FROM python:3.6.6

RUN mkdir /progimage

WORKDIR /progimage

ADD . /progimage/

RUN pip install -r requirements.txt

