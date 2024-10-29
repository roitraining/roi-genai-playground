FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PATH=“${PATH}:/root/.local/bin”

EXPOSE 8080
CMD ["streamlit", "run",  "Chatbot.py"]