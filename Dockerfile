FROM python:alpine

# RUN apk --update add --no-cache bash curl ffmpeg dumb-init gcc libc-dev
RUN apk add --no-cache --virtual build-deps \
      gcc \
      libc-dev && \
    apk add --no-cache \
      ffmpeg \
      dumb-init && \
    pip install --no-cache-dir \
      streamlink \
      requests && \
    apk del build-deps

WORKDIR /app
COPY twitch-recorder.py .
COPY config.py .

# ENTRYPOINT [ "nohup", "python3", "/app/twitch-recorder.py", ">/dev/null", "2>&1" , "&" ]
