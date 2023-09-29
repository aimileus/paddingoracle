FROM python:3

EXPOSE 8080
ENV PYTHONUNBUFFERED=1

COPY "." "/src"

RUN ["pip", "install", "/src"]

ENTRYPOINT ["paddingoracle"]