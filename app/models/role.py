# app/models/role.py
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

class Role(Base):
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Relationship to users (one-to-many)
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

# UserRole table no longer needed - using direct foreign key in User model