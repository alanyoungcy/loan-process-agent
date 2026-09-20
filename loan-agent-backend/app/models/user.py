"""
User Model - Authentication and authorization
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.base import Base


class User(Base):
    """
    User Model

    Represents system users with authentication and role-based access
    """
    __tablename__ = "users"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)

    # Authentication
    hashed_password = Column(String(200), nullable=False)

    # Profile information
    full_name = Column(String(200), nullable=False)

    # Role and permissions
    role = Column(String(50), nullable=False, default="collector")
    # Roles: admin, supervisor, collector

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False)

    # Tracking
    last_login = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin" or self.is_superuser

    @property
    def is_supervisor(self) -> bool:
        """Check if user is supervisor or higher"""
        return self.role in ["admin", "supervisor"] or self.is_superuser

    @property
    def is_collector(self) -> bool:
        """Check if user is a collector"""
        return self.role == "collector"
