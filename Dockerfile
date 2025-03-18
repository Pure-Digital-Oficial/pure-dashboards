FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD sh -c "streamlit run src/main.py --server.port=${PORT:-8501} --server.address=0.0.0.0"
