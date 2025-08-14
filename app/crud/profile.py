# app/crud/profile.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate
from .base import CRUDBase

class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: UUID) -> Optional[Profile]:
        """Get profile by user ID with user information"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .filter(Profile.user_id == user_id)
            .first()
        )
    
    def create_for_user(self, db: Session, *, user_id: UUID, obj_in: ProfileCreate) -> Profile:
        """Create a profile for a specific user"""
        create_data = obj_in.dict()
        create_data["user_id"] = user_id
        
        db_obj = Profile(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_profiles_with_pictures(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles that have profile pictures"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .filter(Profile.profile_picture_url.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_complete_profiles(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles that are considered complete (have bio and picture)"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .filter(Profile.bio.isnot(None))
            .filter(Profile.profile_picture_url.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_profiles_with_emergency_contact(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles that have emergency contact information"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .filter(Profile.emergency_contact.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_preference(self, db: Session, *, profile: Profile, key: str, value: Any) -> Profile:
        """Update a single preference"""
        if not profile.preferences:
            profile.preferences = {}
        
        profile.preferences[key] = value
        # Mark the JSONB field as modified
        db.merge(profile)
        db.commit()
        db.refresh(profile)
        return profile
    
    def remove_preference(self, db: Session, *, profile: Profile, key: str) -> Profile:
        """Remove a preference"""
        if profile.preferences and key in profile.preferences:
            del profile.preferences[key]
            # Mark the JSONB field as modified
            db.merge(profile)
            db.commit()
            db.refresh(profile)
        return profile
    
    def get_preference(self, profile: Profile, key: str, default=None):
        """Get a specific preference value"""
        if not profile.preferences:
            return default
        return profile.preferences.get(key, default)
    
    def search_by_bio(self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Search profiles by bio content"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .filter(Profile.bio.ilike(f"%{search_term}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_profiles_by_role(self, db: Session, *, role_name: str, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get profiles of users with specific role"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user).joinedload(User.roles))
            .join(Profile.user)
            .join(User.roles)
            .filter(User.roles.any(name=role_name))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_complete_profiles(self, db: Session) -> int:
        """Count profiles that are complete"""
        return (
            db.query(Profile)
            .filter(Profile.bio.isnot(None))
            .filter(Profile.profile_picture_url.isnot(None))
            .count()
        )
    
    def count_profiles_with_emergency_contact(self, db: Session) -> int:
        """Count profiles with emergency contact"""
        return (
            db.query(Profile)
            .filter(Profile.emergency_contact.isnot(None))
            .count()
        )
    
    def get_all_with_user(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Profile]:
        """Get all profiles with user information"""
        return (
            db.query(Profile)
            .options(joinedload(Profile.user))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def update_profile_picture(self, db: Session, *, profile: Profile, picture_url: str) -> Profile:
        """Update only the profile picture URL"""
        profile.profile_picture_url = picture_url
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    
    def update_bio(self, db: Session, *, profile: Profile, bio: str) -> Profile:
        """Update only the bio"""
        profile.bio = bio
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

profile_crud = CRUDProfile(Profile)