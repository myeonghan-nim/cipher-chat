# ======= Builder Stage =======
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ======= Final Stage =======
FROM python:3.12-slim AS final

WORKDIR /work

COPY --from=builder /install /usr/local

COPY app app
COPY entrypoint.sh .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
