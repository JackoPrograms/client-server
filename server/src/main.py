from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import Teachers, Students, Group, Request, Stage
from pydantic import BaseModel
from datetime import date
import json
import os

# Удаляем старые таблицы с использованием CASCADE
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Модель для создания группы
class GroupCreate(BaseModel):
    name: str
    teacher_id: int

    class Config:
        orm_mode = True

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Вспомогательные функции
def create_group(db: Session, teacher_id: int):
    group_name = f"Group {teacher_id}-{db.query(Group).filter(Group.teacher_id == teacher_id).count() + 1}"
    new_group = Group(name=group_name, teacher_id=teacher_id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

def is_group_full(db: Session, group_id: int):
    return db.query(Students).filter(Students.group_id == group_id).count() >= 10

def enroll_student(db: Session, student_data: dict):
    teacher_id = student_data.get("teacher_id")
    if not teacher_id:
        raise ValueError("Teacher ID is required")

    # Находим преподавателя, к которому привязывается студент
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise ValueError("Teacher not found")

    # Находим всех преподавателей на той же кафедре
    department_teachers = db.query(Teachers).filter(
        Teachers.department == teacher.department
    ).all()

    # Ищем все группы на кафедре с менее чем 10 студентами
    groups_with_space = []
    for group in db.query(Group).join(Teachers).filter(
        Teachers.department == teacher.department
    ).all():
        student_count = db.query(Students).filter(Students.group_id == group.id).count()
        if student_count < 10:
            groups_with_space.append(group)

    # Если есть группы с незаполненными местами, добавляем студента в первую такую группу
    if groups_with_space:
        group = groups_with_space[0]  # Берём первую группу с незаполненными местами
        new_student = Students(
            name=student_data.get("name"),
            department=student_data.get("department"),
            group_id=group.id,
            photo=student_data.get("photo"),
            date_of_birth=student_data.get("date_of_birth"),
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student

    # Если все группы заполнены, создаем новую группу
    # Выбираем преподавателя с наименьшим количеством групп
    teacher_with_min_groups = min(
        department_teachers,
        key=lambda t: db.query(Group).filter(Group.teacher_id == t.id).count()
    )

    # Создаем новую группу для выбранного преподавателя
    new_group = create_group(db, teacher_with_min_groups.id)

    # Создаем студента и привязываем его к новой группе
    new_student = Students(
        name=student_data.get("name"),
        department=student_data.get("department"),
        group_id=new_group.id,
        photo=student_data.get("photo"),
        date_of_birth=student_data.get("date_of_birth"),
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


def expel_student(db: Session, student_id: int):
    student = db.query(Students).filter(Students.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    group_id = student.group_id
    db.delete(student)
    db.commit()

    # Удаляем группу, если она пуста
    if db.query(Students).filter(Students.group_id == group_id).count() == 0:
        db.query(Group).filter(Group.id == group_id).delete()
        db.commit()

def redistribute_students(db: Session, teacher_id: int):
    # Находим уволенного преподавателя
    teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
    if not teacher:
        raise ValueError("Teacher not found")

    # Находим всех преподавателей той же кафедры
    department_teachers = db.query(Teachers).filter(
        Teachers.department == teacher.department,
        Teachers.id != teacher_id  # Исключаем уволенного преподавателя
    ).all()

    if not department_teachers:
        raise ValueError("No other teachers in the department")

    # Находим все группы уволенного преподавателя
    groups = db.query(Group).filter(Group.teacher_id == teacher_id).all()

    # Собираем всех студентов из групп уволенного преподавателя
    students_to_redistribute = []
    for group in groups:
        students_in_group = db.query(Students).filter(Students.group_id == group.id).all()
        students_to_redistribute.extend(students_in_group)

    # Распределяем студентов поровну между преподавателями
    teacher_index = 0
    for student in students_to_redistribute:
        # Находим группы текущего преподавателя
        current_teacher = department_teachers[teacher_index]
        teacher_groups = db.query(Group).filter(Group.teacher_id == current_teacher.id).all()

        # Ищем группу с свободными местами
        placed = False
        for group in teacher_groups:
            if db.query(Students).filter(Students.group_id == group.id).count() < 10:
                # Если в группе есть свободное место, перемещаем студента
                student.group_id = group.id
                db.commit()
                placed = True
                break

        # Если свободных мест в группах текущего преподавателя нет, создаем новую группу
        if not placed:
            new_group = create_group(db, current_teacher.id)
            student.group_id = new_group.id
            db.commit()

        # Переходим к следующему преподавателю
        teacher_index = (teacher_index + 1) % len(department_teachers)

    # Удаляем группы уволенного преподавателя
    for group in groups:
        db.delete(group)
    db.commit()

# @app.delete("/teachers/{teacher_id}")
# def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
#     teacher = db.query(Teachers).filter(Teachers.id == teacher_id).first()
#     if not teacher:
#         raise HTTPException(status_code=404, detail="Teacher not found")

#     # Перераспределяем группы
#     redistribute_groups(db, teacher_id)

#     # Удаляем преподавателя
#     db.delete(teacher)
#     db.commit()
#     return {"message": "Teacher deleted"}

# Маршруты
@app.post("/groups/")
def create_group_endpoint(group: GroupCreate, db: Session = Depends(get_db)):
    teacher = db.query(Teachers).filter(Teachers.id == group.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if not group.name:
        group_name = f"Group {group.teacher_id}-{db.query(Group).filter(Group.teacher_id == group.teacher_id).count() + 1}"
    else:
        group_name = group.name

    new_group = Group(name=group_name, teacher_id=group.teacher_id)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@app.post("/students/")
def create_student(student_data: dict, db: Session = Depends(get_db)):
    try:
        new_student = enroll_student(db, student_data)
        return new_student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/students/")
def read_students(department: str = None, group_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Students)
    
    if department:
        query = query.filter(Students.department == department)
    
    if group_id:
        query = query.filter(Students.group_id == group_id)

    students = query.all()
    return students

def teacher_to_dict(teacher):
    return {
        "id": teacher.id,
        "uuid": str(teacher.uuid),
        "name": teacher.name,
        "department": teacher.department,
        "photo": teacher.photo,
        "date_of_birth": teacher.date_of_birth.isoformat() if teacher.date_of_birth else None,
        "created_at": teacher.created_at.isoformat() if teacher.created_at else None,
        "groups": [group.name for group in teacher.groups]  # Добавляем список групп преподавателя
    }

def student_to_dict(student):
    return {
        "id": student.id,
        "uuid": str(student.uuid),
        "name": student.name,
        "department": student.department,
        "group_id": student.group_id,
        "group_name": student.group.name if student.group else None,  # Название группы
        "photo": student.photo,
        "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else None,
        "created_at": student.created_at.isoformat() if student.created_at else None
    }

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket подключен")

    db = SessionLocal()  # Открываем сессию БД

    try:
        # При первом подключении отправляем актуальные данные
        teachers = db.query(Teachers).order_by(Teachers.id).all()
        students = db.query(Students).order_by(Students.id).all()

        await websocket.send_text(json.dumps({
            'teachers': [teacher_to_dict(teacher) for teacher in teachers],
            'students': [student_to_dict(student) for student in students],
        }))

        while True:
            # Ожидаем сообщение от клиента
            data = await websocket.receive_text()
            print(f"Получено сообщение: {data}")

            try:
                # Разбираем JSON-строку
                request_data = json.loads(data)

                if request_data.get("action") == "create":
                    print("Создание нового элемента:", request_data)  # Логируем данные
                    name = request_data.get("name")
                    department = request_data.get("department")
                    photo = request_data.get("photo")
                    date_of_birth = request_data.get("dateOfBirth")
                    if date_of_birth:
                        date_of_birth = date.fromisoformat(date_of_birth)  # Преобразуем строку в объект date

                    if request_data.get("type") == "teacher":
                        # Создаем нового преподавателя
                        new_item = Teachers(
                            name=name,
                            department=department,
                            photo=photo,
                            date_of_birth=date_of_birth
                        )
                        db.add(new_item)
                        db.commit()  # Сохраняем изменения в базе данных
                        print(f"Новый преподаватель добавлен: {new_item}")
                    else:
                        # Создаем нового студента
                        # Проверяем, есть ли в системе преподаватели
                        first_teacher = db.query(Teachers).order_by(Teachers.id).first()
                        if not first_teacher:
                            raise ValueError("Невозможно создать студента: в системе нет преподавателей")

                        # Используем функцию enroll_student для автоматического создания группы
                        student_data = {
                            "name": name,
                            "department": department,
                            "photo": photo,
                            "date_of_birth": date_of_birth,
                            "teacher_id": first_teacher.id  # Привязываем студента к первому преподавателю
                        }
                        new_student = enroll_student(db, student_data)
                        print(f"Новый студент добавлен: {new_student}")

                elif request_data.get("action") == "fire":
                    # Удаляем преподавателя или студента из базы данных
                    item_id = request_data.get("id")
                    if request_data.get("type") == "teacher":
                        item_to_delete = db.query(Teachers).filter(Teachers.id == item_id).first()
                    else:
                        item_to_delete = db.query(Students).filter(Students.id == item_id).first()

                    if item_to_delete:
                        if request_data.get("type") == "teacher":
                            # Проверяем, есть ли студенты на кафедре этого преподавателя
                            students_in_department = db.query(Students).filter(Students.department == item_to_delete.department).count()
                            teachers_in_department = db.query(Teachers).filter(Teachers.department == item_to_delete.department).count()

                            if students_in_department > 0 and teachers_in_department <= 1:
                                # Если есть студенты и это последний преподаватель, запрещаем удаление
                                print(f"Нельзя уволить последнего преподавателя на кафедре {item_to_delete.department}, пока там есть студенты.")
                                await websocket.send_text(json.dumps({
                                    'error': 'Нельзя уволить последнего преподавателя на кафедре, пока там есть студенты.',
                                    'teachers': [teacher_to_dict(teacher) for teacher in db.query(Teachers).all()],
                                    'students': [student_to_dict(student) for student in db.query(Students).all()],
                                }))
                                continue  # Пропускаем удаление

                            # Если студентов нет, или это не последний преподаватель, перераспределяем студентов (если есть)
                            if students_in_department > 0:
                                try:
                                    redistribute_students(db, item_to_delete.id)
                                except ValueError as e:
                                    await websocket.send_text(json.dumps({"error": str(e)}))
                                    continue

                            # Удаляем преподавателя
                            db.delete(item_to_delete)
                            db.commit()
                            print(f"Преподаватель с ID {item_id} удалён из базы данных")
                        else:
                            # Удаляем студента
                            group_id = item_to_delete.group_id  # Получаем ID группы студента
                            db.delete(item_to_delete)
                            db.commit()
                            print(f"Студент с ID {item_id} удалён из базы данных")

                            # Проверяем, остались ли студенты в группе
                            students_in_group = db.query(Students).filter(Students.group_id == group_id).count()
                            if students_in_group == 0:
                                # Если студентов в группе больше нет, удаляем группу
                                group_to_delete = db.query(Group).filter(Group.id == group_id).first()
                                if group_to_delete:
                                    db.delete(group_to_delete)
                                    db.commit()
                                    print(f"Группа с ID {group_id} удалена, так как в ней больше нет студентов")
                    else:
                        print(f"Элемент с ID {item_id} не найден")
                elif request_data.get("action") == "update":
                    # Обновляем существующую запись
                    item_id = request_data.get("id")
                    if request_data.get("type") == "teacher":
                        item_to_update = db.query(Teachers).filter(Teachers.id == item_id).first()
                    else:
                        item_to_update = db.query(Students).filter(Students.id == item_id).first()

                    if item_to_update:
                        item_to_update.name = request_data.get("name")
                        item_to_update.department = request_data.get("department")
                        item_to_update.group = request_data.get("group")
                        item_to_update.photo = request_data.get("photo")
                        item_to_update.date_of_birth = request_data.get("dateOfBirth")  # Обновляем дату рождения
                        db.commit()
                        print(f"Элемент с ID {item_id} обновлён")
                    else:
                        print(f"Элемент с ID {item_id} не найден")

                # Получаем обновленные данные и сортируем их
                teachers = db.query(Teachers).order_by(Teachers.id).all()
                students = db.query(Students).order_by(Students.id).all()

                # Отправляем обновленные данные всем подключенным клиентам
                await websocket.send_text(json.dumps({
                    'teachers': [teacher_to_dict(teacher) for teacher in teachers],
                    'students': [student_to_dict(student) for student in students],
                }))
            except json.JSONDecodeError as e:
                print(f"Ошибка при разборе JSON: {e}")
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
            except ValueError as e:
                print(f"Ошибка в данных: {e}")
                await websocket.send_text(json.dumps({"error": str(e)}))
            except Exception as e:
                print(f"Ошибка при обработке данных: {e}")
                db.rollback()  # Откатываем изменения в случае ошибки
                await websocket.send_text(json.dumps({"error": "Internal server error"}))

    except WebSocketDisconnect:
        print("WebSocket отключен")
    finally:
        db.close()  # Закрываем сессию БД