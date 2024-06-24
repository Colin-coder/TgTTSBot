FROM python:3-alpine3.14
WORKDIR /app
ENV TG_CHAT_ID=1057462948
ENV TG_API_TOKEN=7140456051:AAFb5imnrw5RInzj-A0ElGo6fY5OV-N8N2Y
RUN apk add gcc python3-dev linux-headers libc-dev libffi libffi-dev --no-cache
RUN pip install poetry==1.7.0
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install
COPY . .
CMD ["sh","-c","poetry run python main.py"]
