# Text Scanner Microservices

Полностью готовый к запуску учебный проект, реализующий микросервис для хранения текстовых отчётов, 
их анализа и визуализации «облако слов».

После старта будут доступны:

| URL | Сервис |
|-----|--------|
| http://localhost:8000/docs | API Gateway (Swagger) |
| http://localhost:8081/docs | File Storing Service |
| http://localhost:8082/docs | File Analysis Service |
| http://localhost:9001 | MinIO Console (login *minio* / *minio123*) |

> Все сервисы написаны на **FastAPI**, а файлы хранятся в **MinIO**. Базы данных — PostgreSQL.

### Тесты

```bash
docker compose run --rm analysis pytest --cov=.
```
