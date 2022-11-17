FROM python:3.9.15-buster
RUN  echo "deb https://deb.debian.org/debian/  bullseye main" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install -y \
 		sqlite3 \
  	&& rm -rf /var/lib/apt/lists/*
#echo "deb https://deb.debian.org/debian/  bullseye main" >> /etc/apt/sources.list \
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python setup.py install
EXPOSE 9090
CMD [ "python", "server.py" ]

