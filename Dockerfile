FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir liquid-audio "liquid-audio[demo]"

COPY . .

CMD ["python"]
