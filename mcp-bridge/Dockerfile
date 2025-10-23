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

# Add helm repos with correct URLs
RUN helm repo add jenkins https://charts.jenkins.io \
    && helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts \
    && helm repo add argo https://argoproj.github.io/argo-helm \
    && helm repo update

COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY . .

# Fix kubeconfig permissions and create directory
RUN mkdir -p /root/.kube && chmod 400 /root/.kube


EXPOSE 9000

# Fix kubeconfig permissions at runtime and start the bridge
CMD ["sh", "-c", "chmod 400 /root/.kube/config 2>/dev/null || true && python bridge.py"]