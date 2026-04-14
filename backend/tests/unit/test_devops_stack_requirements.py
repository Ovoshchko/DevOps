from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding='utf-8')


def test_backend_health_reports_ok_when_postgres_and_influx_are_available(monkeypatch):
    monkeypatch.setattr('backend.app.main.is_postgres_available', lambda: True)
    monkeypatch.setattr('backend.app.main.is_influx_available', lambda: True)
    monkeypatch.setattr('backend.app.main.is_postgres_configured', lambda: True)

    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'postgres_configured': True,
        'postgres_available': True,
        'influx_available': True,
    }


def test_backend_health_reports_degraded_when_a_dependency_is_unavailable(monkeypatch):
    monkeypatch.setattr('backend.app.main.is_postgres_available', lambda: False)
    monkeypatch.setattr('backend.app.main.is_influx_available', lambda: True)
    monkeypatch.setattr('backend.app.main.is_postgres_configured', lambda: True)

    client = TestClient(app)
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json()['status'] == 'degraded'
    assert response.json()['postgres_available'] is False
    assert response.json()['influx_available'] is True


def test_backend_metrics_endpoint_exposes_prometheus_metrics():
    client = TestClient(app)

    response = client.get('/metrics')

    assert response.status_code == 200
    assert 'backend_http_requests_total' in response.text
    assert 'backend_http_request_duration_seconds' in response.text


def test_docker_compose_defines_complete_lab2_stack():
    compose = _read_text('docker-compose.yml')
    frontend_nginx = _read_text('frontend/nginx/default.conf')

    assert 'influxdb:' in compose
    assert 'postgres:' in compose
    assert 'ml-service:' in compose
    assert 'backend:' in compose
    assert 'frontend:' in compose
    assert 'POSTGRES_DSN:' in compose
    assert 'ML_SERVICE_URL:' in compose
    assert 'depends_on:' in compose
    assert 'healthcheck:' in compose
    assert 'postgres-data:' in compose
    assert 'influxdb-data:' in compose
    assert 'prometheus:' in compose
    assert 'grafana:' in compose
    assert '9090:9090' in compose
    assert '3001:3000' in compose
    assert 'proxy_pass http://backend:8000/;' in frontend_nginx


def test_backend_and_frontend_dockerfiles_cover_runtime_requirements():
    backend_dockerfile = _read_text('backend/Dockerfile')
    frontend_dockerfile = _read_text('frontend/Dockerfile')
    ml_dockerfile = _read_text('ml-service/Dockerfile')
    frontend_nginx = _read_text('frontend/nginx/default.conf')
    backend_pyproject = _read_text('backend/pyproject.toml')
    frontend_package = _read_text('frontend/package.json')
    ml_pyproject = _read_text('ml-service/pyproject.toml')

    assert 'FROM python:3.11-slim AS builder' in backend_dockerfile
    assert 'CMD ["uvicorn", "app.main:app"' in backend_dockerfile
    assert 'EXPOSE 8000' in backend_dockerfile
    assert 'fastapi>=' in backend_pyproject
    assert 'psycopg[binary]>=' in backend_pyproject
    assert 'httpx>=' in backend_pyproject

    assert 'FROM node:20-alpine AS builder' in frontend_dockerfile
    assert 'RUN npm run build' in frontend_dockerfile
    assert 'FROM nginx:alpine' in frontend_dockerfile
    assert 'EXPOSE 80' in frontend_dockerfile
    assert 'COPY nginx/default.conf /etc/nginx/conf.d/default.conf' in frontend_dockerfile
    assert '"build": "react-scripts build"' in frontend_package
    assert '"test": "react-scripts test --watchAll=false"' in frontend_package
    assert '"typecheck": "tsc --noEmit"' in frontend_package
    assert 'proxy_pass http://backend:8000/;' in frontend_nginx
    assert 'try_files $uri /index.html;' in frontend_nginx

    assert 'COPY models ./models' in ml_dockerfile
    assert 'CMD ["uvicorn", "app.main:app"' in ml_dockerfile
    assert 'EXPOSE 8001' in ml_dockerfile
    assert 'scikit-learn>=' in ml_pyproject
    assert 'joblib>=' in ml_pyproject


def test_production_compose_and_nginx_support_containerized_deployment():
    prod_compose = _read_text('docker-compose.prod.yml')
    nginx_conf = _read_text('nginx/default.conf')
    prometheus_config = _read_text('prometheus/prometheus.yml')
    grafana_datasource = _read_text('grafana/provisioning/datasources/prometheus.yml')
    grafana_dashboard_provider = _read_text('grafana/provisioning/dashboards/dashboard-provider.yml')

    assert 'ghcr.io/' in prod_compose
    assert 'traffic-backend:latest' in prod_compose
    assert 'traffic-frontend:latest' in prod_compose
    assert 'traffic-ml-service:latest' in prod_compose
    assert './nginx:/etc/nginx/conf.d:ro' in prod_compose

    assert 'location /api/' in nginx_conf
    assert 'proxy_pass http://backend:8000/;' in nginx_conf
    assert 'try_files $uri /index.html;' in nginx_conf
    assert "job_name: 'backend'" in prometheus_config
    assert "job_name: 'ml-service'" in prometheus_config
    assert 'backend:8000' in prometheus_config
    assert 'ml-service:8001' in prometheus_config
    assert 'url: http://prometheus:9090' in grafana_datasource
    assert 'path: /var/lib/grafana/dashboards' in grafana_dashboard_provider


def test_terraform_and_ansible_files_cover_lab2_infrastructure_tasks():
    terraform_main = _read_text('terraform/yandex/main.tf')
    terraform_variables = _read_text('terraform/yandex/variables.tf')
    terraform_outputs = _read_text('terraform/yandex/outputs.tf')
    install_docker = _read_text('ansible/install_docker.yml')
    deploy_app = _read_text('ansible/deploy_app.yml')

    assert 'resource "yandex_compute_instance" "vm"' in terraform_main
    assert 'resource "yandex_vpc_network" "network"' in terraform_main
    assert 'nat       = true' in terraform_main
    assert 'variable "ssh_public_key_path"' in terraform_variables
    assert 'output "external_ip"' in terraform_outputs

    assert 'name: Install Docker' in install_docker
    assert 'docker-ce' in install_docker
    assert 'docker-compose-plugin' in install_docker
    assert 'name: Deploy application' in deploy_app
    assert 'docker compose -f {{ app_dir }}/docker-compose.prod.yml pull' in deploy_app
    assert 'docker compose -f {{ app_dir }}/docker-compose.prod.yml up -d' in deploy_app


def test_ci_pipeline_covers_lab1_and_lab2_build_test_and_registry_requirements():
    workflow = _read_text('.github/workflows/traffic-ci.yml')

    assert 'backend-test:' in workflow
    assert 'frontend-test:' in workflow
    assert 'backend-build:' in workflow
    assert 'frontend-build:' in workflow
    assert 'ml-test:' in workflow
    assert 'ml-build:' in workflow
    assert 'backend-docker:' in workflow
    assert 'frontend-docker:' in workflow
    assert 'ml-docker:' in workflow
    assert 'docker/login-action@v3' in workflow
    assert 'docker/build-push-action@v6' in workflow
    assert 'ghcr.io/${{ env.OWNER }}/traffic-backend:latest' in workflow


def test_readme_describes_required_lab1_architecture_and_validation_flow():
    readme = _read_text('README.md')
    vm_init = _read_text('init_vm.sh')

    assert 'FastAPI REST API' in readme
    assert 'React web client' in readme
    assert 'PostgreSQL' in readme
    assert 'InfluxDB' in readme
    assert 'docker compose up -d --build' in readme
    assert 'python -m pytest -q backend/tests' in readme
    assert 'npm run typecheck && npm test && npm run build' in readme
    assert 'terraform -chdir=terraform/yandex validate' in vm_init
    assert 'terraform -chdir=terraform/yandex apply' in vm_init
    assert 'ansible/inventory.ini' in vm_init
    assert 'Prometheus: `http://localhost:9090`' in readme
    assert 'Grafana: `http://localhost:3001`' in readme
