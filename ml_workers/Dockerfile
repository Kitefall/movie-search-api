FROM python:3.9.13-slim
WORKDIR /ml_workers
COPY requirements.txt /ml_workers
RUN pip install --upgrade pip && pip install -r /ml_workers/requirements.txt
CMD ["python", "worker.py"]