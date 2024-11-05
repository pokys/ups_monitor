FROM python:3.12-slim

# copy requirements.txt and ups.py
COPY requirements.txt .
COPY ups.py .

# install snmpwalk
RUN apt-get update && apt-get install -y snmp && rm -rf /var/lib/apt/lists/*
# install python requirements
RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /app
CMD ["python", "ups.py"]
