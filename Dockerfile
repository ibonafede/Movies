FROM python:3.9-slim
COPY ./app /usr/local/app
COPY ./requirements.txt /usr/local/app/
WORKDIR /usr/local/app/src
RUN pip install -r /usr/local/app/requirements.txt
EXPOSE 8000
CMD ["uvicorn","main:app","--host=0.0.0.0", "--reload"]