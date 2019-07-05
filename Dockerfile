FROM python:3-slim

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY notarisation.py ./
COPY okeydokey ./okeydokey/


CMD [ "python", "./notarisation.py" ]
