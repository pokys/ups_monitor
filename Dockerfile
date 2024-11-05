FROM python:3.12-slim
WORKDIR /app

# copy requirements.txt and ups.py
COPY requirements.txt /app/
COPY ups.py /app/

# install snmpwalk
RUN apt-get update && apt-get install -y snmp && rm -rf /var/lib/apt/lists/*
# install python requirements
RUN pip install --no-cache-dir -r requirements.txt



CMD ["python", "/app/ups.py"]
