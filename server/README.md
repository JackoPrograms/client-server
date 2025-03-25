# server

## Project Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Compile and Hot-Reload for Development

```sh
uvicorn src.main:app --reload
```

<!-- Добавление пользователя в БД -->
```sh
curl -X POST "http://localhost:8000/students/" -H "Content-Type: application/json" -d '{"name": "Петров Петр Петрович", "department": "Кафедра 2", "group": "Группа 2"}'
```

<!-- Получение информации из таблицы -->
```sh
curl "http://localhost:8000/students/?department=Kafedra%201&group=Gruppa%201"
```