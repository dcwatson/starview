FROM python:alpine

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt /starview/
RUN mkdir -p /data && \
    pip install --no-cache-dir -Ur /starview/requirements.txt

COPY . /starview

WORKDIR /starview

VOLUME ["/data"]

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "starview:app"]
