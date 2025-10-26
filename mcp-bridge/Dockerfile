FROM python:3.11-slim

WORKDIR /app

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["python", "bridge.py"]