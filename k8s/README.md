# Kubernetes manifests

These manifests mirror the current compose stack in the `devops` namespace.

Apply in this order:

```bash
kubectl apply -f k8s/frontend/namespace.yaml
kubectl apply -f k8s/secrets/secrets.yaml
kubectl apply -f k8s/postgres/postgres.yaml
kubectl apply -f k8s/influxdb/influxdb.yaml
kubectl apply -f k8s/ml-service/ml-service.yaml
kubectl apply -f k8s/backend/backend.yaml
kubectl apply -f k8s/backend/backend-hpa.yaml
kubectl apply -f k8s/prometheus/prometheus.yaml
kubectl apply -k k8s/grafana
kubectl apply -f k8s/frontend/frontend.yaml
```

Quick checks:

```bash
kubectl -n devops get pods
kubectl -n devops get svc
kubectl -n devops get hpa
```

Important:

- The frontend Nginx config proxies `/api/` to the `backend` service.
- Grafana and frontend are exposed as `LoadBalancer` services.
- If GitHub Container Registry images are private, add an image pull secret before applying the deployments.
- Backend autoscaling requires a working `metrics-server` in the cluster because the HPA targets `15%` average CPU utilization.
- Replace every `change-me` value in `k8s/secrets/secrets.yaml` before applying it to the cluster.
