FROM ubuntu:18.04

# install python
RUN apt-get update && apt-get -y install python3 python3-pip
RUN pip3 install virtualenv
RUN virtualenv /opt/paradox/venv

# setup environmnet variables
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_APP=paradox

# setup virtualenv
WORKDIR /opt/paradox
COPY ./lib ./lib
COPY ./paradox ./paradox
COPY requirements.txt ./
RUN chmod 700 ./entrypoint.sh
COPY entrypoint.sh ./
RUN /bin/bash -c ". venv/bin/activate && pip install --no-cache-dir -r requirements.txt"

CMD [ "/opt/paradox/entrypoint.sh" ]