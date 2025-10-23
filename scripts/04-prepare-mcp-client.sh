
# Ensure the kubeconfig-docker file exists and is world-readable
cp ~/.kube/config ./kube/

# Patch the server address for Kind context to use the Docker network name
KIND_SERVER_LINE=$(grep -n 'server: https://127.0.0.1' ./kube/config | cut -d: -f1)
if [ ! -z "$KIND_SERVER_LINE" ]; then
	sed -i '' "${KIND_SERVER_LINE}s|https://127.0.0.1|https://kind-mcp-lab-control-plane|" ./kube/config
fi


KIND_SERVER_LINE=$(grep -n 'server: https://localhost' ./kube/config | cut -d: -f1)
if [ ! -z "$KIND_SERVER_LINE" ]; then
        sed -i '' "${KIND_SERVER_LINE}s|https://localhost|https://kind-mcp-lab-control-plane|" ./kube/config
fi

# Change any port used for kind to 6443 (standard Kubernetes API port)
sed -i '' 's|kind-mcp-lab-control-plane:[0-9]*|kind-mcp-lab-control-plane:6443|g' ./kube/config



chmod go-rwx ./kube/config 
chmod go-rwx ./kube


#docker exec -it ollama mkdir -p /root/.kube
#docker exec -it ollama bash
# Inside the container:
#docker exec -it ollama curl -LO \"https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\"
#docker exec -it ollama chmod +x kubectl
#docker exec -it ollama mv kubectl /usr/local/bin/
