# app/crud/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        # Update the updated_at timestamp if it exists
        if hasattr(db_obj, 'updated_at'):
            setattr(db_obj, 'updated_at', datetime.utcnow())
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> ModelType:
        """Hard delete a record"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    def soft_delete(self, db: Session, *, id: UUID) -> Optional[ModelType]:
        """Soft delete a record (set deleted_at timestamp)"""
        obj = db.query(self.model).get(id)
        if obj and hasattr(obj, 'deleted_at'):
            obj.deleted_at = datetime.utcnow()
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
    
    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get active records (not soft deleted)"""
        query = db.query(self.model)
        if hasattr(self.model, 'deleted_at'):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.offset(skip).limit(limit).all()
    
    def count(self, db: Session) -> int:
        """Count total records"""
        return db.query(self.model).count()
    
    def count_active(self, db: Session) -> int:
        """Count active records (not soft deleted)"""
        query = db.query(self.model)
        if hasattr(self.model, 'deleted_at'):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.count()