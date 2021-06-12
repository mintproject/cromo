FROM python:3
WORKDIR /app
COPY . .
RUN python setup.py install
EXPOSE 9090
ENTRYPOINT [ "python" ]
CMD [ "server.py" ]
