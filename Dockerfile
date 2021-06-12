FROM python:3.9-alpine
RUN apk update && apk add gcc python3-dev musl-dev g++ 
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python setup.py install
EXPOSE 9090
CMD [ "python", "server.py" ]

