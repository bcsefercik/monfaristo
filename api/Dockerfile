FROM python:3.9.19-slim

RUN mkdir /service
RUN mkdir /service/api_service
COPY api/requirements.txt /service/api_service/requirements.txt
WORKDIR /service/api_service
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY api/ .

EXPOSE 8000

ENTRYPOINT [ "uvicorn", "main:app", "--port", "8000", "--workers", "2", "--reload" ]