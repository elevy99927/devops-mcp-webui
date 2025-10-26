FROM python:3.11-slim

WORKDIR /app

# Install kubectl, helm and ca-certificates
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    wget \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && wget https://get.helm.sh/helm-v3.13.0-linux-amd64.tar.gz \
    && tar -zxvf helm-v3.13.0-linux-amd64.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && rm -rf helm-v3.13.0-linux-amd64.tar.gz linux-amd64 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add helm repos
RUN helm repo add jenkins https://charts.jenkins.io \
    && helm repo add bitnami https://repo.broadcom.com/bitnami-files \
    && helm repo update

COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

# Fix kubeconfig permissions and create directory
RUN mkdir -p /root/.kube && chmod 700 /root/.kube

EXPOSE 8080

# Fix kubeconfig permissions at runtime and start the MCP server
CMD ["sh", "-c", "chmod 600 /root/.kube/config 2>/dev/null || true && python server.py"]