# EmberLearn Frontend

AI-powered Python tutoring platform frontend built with Next.js 15, TypeScript, and Monaco Editor.

## Features

- **Monaco Editor**: Full-featured Python code editor with syntax highlighting
- **AI Tutoring**: Chat interface connected to 6 specialized AI agents
- **Progress Tracking**: Visual mastery dashboard with color-coded levels
- **Exercise System**: Auto-generated coding challenges with instant feedback

## Development

```bash
npm install
npm run dev
```

## Production Build

```bash
npm run build
npm start
```

## Docker

```bash
docker build -t emberlearn/frontend:latest .
docker run -p 3000:3000 emberlearn/frontend:latest
```

## Kubernetes Deployment

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl port-forward svc/emberlearn-frontend 3000:80
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8080`)
