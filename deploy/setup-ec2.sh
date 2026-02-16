#!/bin/bash
# =============================================================================
# EC2 Setup Script for BigSpring Knowledge Search Agent
# Run this on a fresh Ubuntu 22.04+ EC2 instance
# =============================================================================
set -e

echo "=== Updating system packages ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== Installing Docker ==="
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow current user to run docker without sudo
sudo usermod -aG docker $USER

echo "=== Installing Git ==="
sudo apt-get install -y git

echo "=== Setup complete ==="
echo ""
echo "IMPORTANT: Log out and back in for docker group to take effect, then:"
echo "  1. Clone your repo:  git clone <your-repo-url> && cd BigSpring_AI_take_home"
echo "  2. Set your API key: echo 'OPENAI_API_KEY=sk-...' > backend/.env"
echo "  3. Deploy:           docker compose up --build -d"
echo "  4. View logs:        docker compose logs -f"
echo ""
echo "The app will be available at http://<your-ec2-public-ip>"
