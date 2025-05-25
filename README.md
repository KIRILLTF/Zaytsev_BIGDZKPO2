# Text Scanner Microservices

Учебный проект на **FastAPI**, демонстрирующий микросервисную архитектуру для хранения текстовых отчётов, их анализа и визуализации «облако слов» с использованием MinIO и PostgreSQL.

---

## 📦 Сервисная архитектура

| URL                           | Описание                                    |
|-------------------------------|---------------------------------------------|
| http://localhost:8000/docs    | **API Gateway** (Swagger)                   |
| http://localhost:8081/docs    | **File Storing Service** (Swagger)          |
| http://localhost:8082/docs    | **File Analysis Service** (Swagger)         |
| http://localhost:9001         | **MinIO Console** (login: `minio` / `minio123`) |

> Все сервисы написаны на **FastAPI**, файлы хранятся в **MinIO**, базы данных — **PostgreSQL**.

---
**Вывод `coverage report -m`:**

| Модуль                        | Stmts | Miss | Cover | Missing                                                     |
| ----------------------------- | ----: | ---: | ----: | ----------------------------------------------------------- |
| `analysis_service/analyse.py` |    13 |    0 | 100 % | —                                                           |
| `analysis_service/main.py`    |    38 |    3 |  92 % | 30, 51, 53                                                  |
| `gateway/main.py`             |    30 |    0 | 100 % | —                                                           |
| `shared/__init__.py`          |     1 |    1 |   0 % | 1                                                           |
| `shared/models.py`            |     7 |    7 |   0 % | 1–11                                                        |
| `shared/schemas.py`           |    17 |   17 |   0 % | 1–19                                                        |
| `storing_service/main.py`     |    88 |   26 |  70 % | 27–28, 38–43, 52–53, 62, 65–70, 78, 91–93, 100–103, 115–117 |
| `tests/test_basic.py`         |     2 |    0 | 100 % | —                                                           |
| `tests/test_services.py`      |   175 |    6 |  97 % | 13–15, 91, 105, 165                                         |
| **TOTAL**                     |   371 |   60 |  84 % | —                                                           |
