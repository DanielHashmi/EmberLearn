# Next.js Kubernetes Deploy - Reference

## Overview

This skill deploys Next.js applications with Monaco Editor integration to Kubernetes, optimized for the EmberLearn frontend.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Ingress                           │   │
│  │              (emberlearn.local)                      │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │                    Service                           │   │
│  │              (emberlearn-frontend)                   │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │              Deployment (2 replicas)                 │   │
│  │  ┌─────────────────┐  ┌─────────────────┐          │   │
│  │  │   Next.js Pod   │  │   Next.js Pod   │          │   │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │          │   │
│  │  │  │  Monaco   │  │  │  │  Monaco   │  │          │   │
│  │  │  │  Editor   │  │  │  │  Editor   │  │          │   │
│  │  │  └───────────┘  │  │  └───────────┘  │          │   │
│  │  └─────────────────┘  └─────────────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Monaco Editor Integration

### SSR-Safe Dynamic Import

Monaco Editor requires browser APIs and cannot be server-side rendered. Use Next.js dynamic imports:

```typescript
import dynamic from 'next/dynamic'

const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
)
```

### Component Structure

```
app/
├── components/
│   ├── CodeEditor.tsx      # Monaco wrapper with SSR disabled
│   ├── ChatPanel.tsx       # AI tutor chat interface
│   └── ProgressDashboard.tsx # Mastery visualization
├── api/
│   ├── execute/route.ts    # Code execution endpoint
│   ├── chat/route.ts       # AI chat endpoint
│   └── progress/route.ts   # Progress data endpoint
└── page.tsx                # Main layout
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API gateway URL |
| `NODE_ENV` | No | Environment (production/development) |

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',  // Required for Docker
  reactStrictMode: true,
  // Disable SSR for Monaco
  transpilePackages: ['@monaco-editor/react'],
}

module.exports = nextConfig
```

## Kubernetes Manifests

### Deployment

Key configurations:
- 2 replicas for high availability
- Resource limits: 512Mi memory, 500m CPU
- Health probes on `/api/health`
- Environment variables from ConfigMap/Secrets

### Service

- ClusterIP type for internal access
- Port 80 → 3000 mapping

### Ingress

- NGINX ingress controller
- Host-based routing
- TLS termination (production)

## Build Process

### Docker Multi-Stage Build

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### Build Commands

```bash
# Local development
npm run dev

# Production build
npm run build

# Docker build
docker build -t emberlearn/frontend:latest .

# Minikube deployment
minikube image load emberlearn/frontend:latest
kubectl apply -f k8s/frontend/
```

## Mastery Level Colors

The frontend uses color-coded mastery levels:

| Level | Range | Color | CSS Class |
|-------|-------|-------|-----------|
| Needs Practice | 0-39% | Red | `mastery-red` |
| Developing | 40-69% | Yellow | `mastery-yellow` |
| Proficient | 70-89% | Green | `mastery-green` |
| Mastered | 90-100% | Blue | `mastery-blue` |

## API Routes

### POST /api/execute

Execute Python code in sandbox.

```typescript
// Request
{ code: string }

// Response
{ output: string, error?: string, executionTime: number }
```

### POST /api/chat

Send message to AI tutor.

```typescript
// Request
{ message: string, context?: object }

// Response
{ response: string, agent: string }
```

### GET /api/progress

Get student progress data.

```typescript
// Response
[{ id, name, mastery, exercisesCompleted, totalExercises }]
```

## Troubleshooting

### Monaco Editor Not Loading

1. Verify dynamic import has `ssr: false`
2. Check browser console for errors
3. Ensure `@monaco-editor/react` is installed

### Build Failures

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules && npm install

# Check TypeScript errors
npm run type-check
```

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -l app=emberlearn-frontend

# View logs
kubectl logs -l app=emberlearn-frontend

# Describe deployment
kubectl describe deployment emberlearn-frontend
```

## Performance Optimization

1. **Code Splitting**: Monaco loads on-demand
2. **Image Optimization**: Use Next.js Image component
3. **Caching**: SWR for data fetching with stale-while-revalidate
4. **CDN**: Static assets served from CDN in production
