# Frontend on Kubernetes

This frontend container already serves the React build through Nginx and proxies `/api/` to `http://backend/`.

Important:

- The backend Kubernetes `Service` must be named `backend`.
- The backend service must live in the same namespace as the frontend.
- If `ghcr.io/ovoshchko/traffic-frontend:latest` is private, create an image pull secret before applying the deployment.

Apply:

```bash
kubectl apply -f k8s/frontend/namespace.yaml
kubectl apply -f k8s/frontend/frontend.yaml
```

Check:

```bash
kubectl -n devops get pods
kubectl -n devops get svc frontend
```
