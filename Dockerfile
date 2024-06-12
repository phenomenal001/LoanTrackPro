FROM python:3.6-jessie
FROM ubuntu:18.04

RUN apt-get -y upgrade
RUN apt-get update && apt-get install -y curl gnupg gnupg2 gnupg1
RUN apt install -y python3-pip
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN apt-get install -y --force-yes unixodbc unixodbc-dev

COPY ./src/ /home/src/

WORKDIR /home/src/

RUN pip3 install --upgrade pip
RUN pip3 install -U pip

RUN pip3 install -r /home/src/requirements.txt

#install install gunicorn
RUN apt install gunicorn -y --force-yes

RUN pip3 install gunicorn

# Expose port 8000 for Gunicorn
EXPOSE 8003

# Start Gunicorn server
#CMD ["gunicorn", "--bind", "0.0.0.0:8002", "--workers", "4", "--env", "FLASK_APP=app:app", "--env", "FLASK_ENV=production", "app:app"]

CMD ["gunicorn", "--bind", "0.0.0.0:8003", "--workers", "2","app:app","--reload"]

#CMD python3 app.py --log=INFO