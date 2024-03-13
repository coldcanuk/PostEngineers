FROM python:3.11-slim
WORKDIR /app
COPY app.py requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#CMD curl -f http://localhost:5000/health || exit 1