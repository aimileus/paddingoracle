FROM python:3

EXPOSE 8080

COPY "." "/src"

RUN ["pip", "install", "/src"]

ENTRYPOINT ["paddingoracle"]