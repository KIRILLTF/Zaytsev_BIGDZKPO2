Вставьте в ваш `README.md` следующий раздел:

## 🧪 Тестирование и отчёт по покрытию

Все ключевые сценарии покрыты юнит- и интеграционными тестами. Порог покрытия установлен на **65 %**, фактически достигнуто **84 %**.

```bash
# в активном виртуальном окружении (.venv)
pip install -r requirements.txt pytest coverage

# запуск тестов
pytest -q

# запуск с измерением покрытия
coverage run --source=. -m pytest -q

# вывод подробного отчёта
coverage report -m
```

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
