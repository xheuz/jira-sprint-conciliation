FROM ubuntu:18.04

# install python
RUN apt-get update && apt-get -y install python3 python3-pip
RUN pip3 install virtualenv
RUN virtualenv /opt/paradox/venv

# setup environmnet variables
ENV JIRA_API=${JIRA_API}
ENV JIRA_USERNAME=${JIRA_USERNAME}
ENV JIRA_PASSWORD=${JIRA_PASSWORD}
ENV FLASK_APP=${FLASK_APP}
ENV FLASK_ENV=${FLASK_ENV}

# setup virtualenv
WORKDIR /opt/paradox
RUN source venv/bin/activate
COPY requirements.txt ./
COPY lib/jiralite-1.0.0.tar.gz ./
RUN pip install --no-cache-dir -r requirements.txt
COPY paradox .

CMD [ "flask run" ]