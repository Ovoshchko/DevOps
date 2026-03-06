# Лабораторная работа №1 (DevOps)

## 1. Цель и контекст

В рамках ЛР1 реализована учебная DevOps-система для анализа аномалий сетевого трафика:
- серверный REST API;
- клиентское веб-приложение;
- ML-сервис;
- постоянное хранение в БД;
- модульные тесты;
- CI-пайплайны в GitHub Actions.

## 2. Состав системы

### 2.1 Компоненты
- `frontend/`: React-приложение (интерфейс оператора).
- `backend/`: FastAPI REST API (бизнес-логика, CRUD детекторов, запуск детекций, мониторинг, генератор).
- `ml-service/`: FastAPI сервис инференса (simple model/fallback scoring).
- `postgres`: операционная БД (конфигурации детекторов, запуски детекций, служебные сущности).
- `influxdb`: time-series БД для входящего сетевого трафика (точки `TrafficPoint`).

### 2.2 Ключевые доменные сущности
- `DetectorConfig`: конфигурация детектора (CRUD в backend).
- `TrafficPoint`: входящие time-series метрики трафика (ingest, не CRUD).
- `DetectionRun`/`DetectionResult`: результат запуска детекции по окну.
- `GeneratorJob`: фоновая генерация synthetic traffic.

## 3. Как работает система

### 3.1 Базовый сценарий
1. Пользователь создаёт/настраивает `DetectorConfig` во вкладке Detectors.
2. Трафик поступает через ingest (или генерируется встроенным генератором).
3. Пользователь запускает Detection Run для выбранного детектора.
4. Backend применяет параметры выбранного детектора (threshold/features/window).
5. Результаты отображаются во вкладках Detections и Monitoring.

### 3.2 REST-взаимодействие
- Frontend общается с Backend только по HTTP REST.
- Backend обращается к ML-service для вычисления anomaly score.
- Backend пишет/читает данные из PostgreSQL и InfluxDB.

### 3.3 Тестирование
- Frontend: unit/snapshot тесты (React Testing Library + Jest).
- Backend: unit/contract/integration тесты (pytest).
- ML-service: unit тесты (pytest).

## 4. Соответствие пунктам задания ЛР1

| Пункт задания | Статус | Что сделано |
|---|---|---|
| Изучить принципы DevOps | Выполнено | В проекте применены практики CI, автоматизация проверки, единый Git workflow, декомпозиция на сервисы |
| Установить и настроить Git | Выполнено | Репозиторий ведётся в Git, структура подготовлена для командной работы |
| RESTful сервис с 4 CRUD | Выполнено | CRUD реализован для `DetectorConfig`: `POST/GET/GET{id}/PUT/DELETE /detectors` |
| Клиентское веб-приложение | Выполнено | Реализован React frontend (детекторы, мониторинг, детекции, генератор) |
| Наличие БД | Выполнено | PostgreSQL + InfluxDB в составе системы |
| Модульные тесты сервера и клиента | Выполнено | Наборы тестов для backend и frontend присутствуют и запускаются |
| REST-коммуникация между сервером и клиентом | Выполнено | Все клиентские операции работают через REST API backend |
| Размещение в VCS (GitHub) | Выполнено | Проект ориентирован на GitHub и GitHub Actions |
| CI: минимум 2 job для сервера (build,test) | Выполнено | `backend-ci.yml`: `test-backend` -> `build-backend` |
| CI: минимум 2 job для клиента (build,test) | Выполнено | `frontend-ci.yml`: `test-frontend` -> `build-frontend` |

## 5. CI/CD и автоматизация

В проекте настроены отдельные workflows:
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `.github/workflows/ml-service-ci.yml`

Особенности:
- В каждом workflow стадийность `test -> build`.
- Запуск только при изменениях в соответствующем сервисе (`paths` filters).
- Проверки выполняются автоматически на `push` и `pull_request`.

## 6. Запуск и проверка

### 6.1 Полный запуск через Docker
1. `docker compose up -d --build`
2. Frontend: `http://localhost:3000`
3. Backend docs: `http://localhost:8000/docs`

### 6.2 Локальная валидация
- Frontend: `cd frontend && npm run typecheck && npm test && npm run build`
- Backend: `PYTHONPATH=. .venv/bin/python -m pytest -q backend/tests`
- ML-service: `PYTHONPATH=ml-service .venv/bin/python -m pytest -q ml-service/tests`

## 7. Итог

Система покрывает все ключевые технические требования ЛР1: REST, web-клиент, БД,
тесты, Git-процесс и CI с обязательными jobs для серверной и клиентской частей.
