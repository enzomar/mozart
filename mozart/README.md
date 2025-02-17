Usage Instructions
Build & Start Containers
sh
Copy
Edit
docker-compose up --build
Update Config (via FastAPI)
sh
Copy
Edit
curl -X POST "http://localhost:8000/config/update" -H "Content-Type: application/json" -d '{"version": "1.1.0", "data": {"settingA": "newValue"}}'
Check Logs
sh
Copy
Edit
docker-compose logs -f
Now, your control plane, sidecar agent, and fake app run in isolated containers with a shared volume for config updates. 🚀