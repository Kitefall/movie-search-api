FROM python:3.9-slim
WORKDIR /gradio_app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r /gradio_app/requirements.txt
COPY requirements.txt /gradio_app
CMD ["python", "gradio_app.py"]
