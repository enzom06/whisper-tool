FROM python:3.11-slim

WORKDIR /opt

COPY . /opt/stt/

WORKDIR /opt/stt/

RUN apt-get update && \
    apt-get install -y --no-install-recommends && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*


RUN chmod +x code/whisper-cpp

CMD python code/main.py


