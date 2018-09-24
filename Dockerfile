FROM markadams/chromium-xvfb-py3

# Install requirements.
ADD ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt