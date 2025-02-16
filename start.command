
#!/bin/bash
echo "Starting Merlin AI..."
cd "$(dirname "$0")"
sudo docker compose up --build
echo "Press any key to exit..."
read -n 1
