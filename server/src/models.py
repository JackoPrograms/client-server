from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, LargeBinary, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    tax = Column(Float, nullable=True)

# class Client(Base):
#     __tablename__ = 'clients'
    
#     id = Column(Integer, primary_key=True, index=True)
#     uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)  # Это обеспечит автоматическую генерацию UUID
#     name = Column(String(100), nullable=False)
#     created_at = Column(TIMESTAMP, server_default=func.now())
    
#     department = Column(String, nullable=True)  # Добавить department
#     group = Column(String, nullable=True)  # Добавить group

#     # Добавляем связь с таблицей Request
#     requests = relationship("Request", back_populates="client")


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete="CASCADE"), nullable=False)

    # Связь с таблицей Students
    students = relationship("Students", back_populates="group")

    # Связь с таблицей Teachers
    teacher = relationship("Teachers", back_populates="groups")

class Teachers(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    department = Column(String, nullable=True)
    photo = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)

    # Связь с таблицей Group (один преподаватель может вести несколько групп)
    groups = relationship("Group", back_populates="teacher")

    # Связь с таблицей Request
    requests = relationship("Request", back_populates="teacher")  # Добавьте эту строку

class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    department = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    photo = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    
    # Связь с таблицей Group
    group = relationship("Group", back_populates="students")

    # Связь с таблицей Request
    requests = relationship("Request", back_populates="student")  # Добавьте эту строку

class Request(Base):
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey('teachers.id', ondelete="CASCADE"), nullable=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete="CASCADE"), nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Связи
    teacher = relationship("Teachers", back_populates="requests")  # Связь с преподавателями
    student = relationship("Students", back_populates="requests")  # Связь со студентами
    stages = relationship("Stage", back_populates="request")  # Связь с этапами (если требуется)

class Stage(Base):
    __tablename__ = 'stages'
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('requests.id', ondelete="CASCADE"), nullable=False)
    stage_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    
    request = relationship("Request", back_populates="stages")