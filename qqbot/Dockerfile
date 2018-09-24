FROM python:3

RUN apt-get update
RUN apt-get install -y proxychains

# Install requirements.
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD ./proxychains.conf /etc/proxychains.conf
ADD ./openssl.py /usr/local/lib/python3.7/site-packages/shadowsocks/crypto/openssl.py