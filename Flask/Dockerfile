# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.7.6
COPY . /app
WORKDIR /app
RUN apt update -y && apt upgrade -y
RUN apt install build-essential libevent-dev unixodbc-dev -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt update -y
RUN ACCEPT_EULA=Y apt install msodbcsql17 -y

RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]
