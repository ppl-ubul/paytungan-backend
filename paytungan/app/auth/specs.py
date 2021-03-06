from dataclasses import dataclass
from typing import List, Optional

from .models import User


@dataclass
class GetUserListSpec:
    user_ids: Optional[List[int]] = None
    usernames: Optional[List[int]] = None
    firebase_uids: Optional[List[int]] = None


@dataclass
class GetUserListResult:
    users: List[User]


@dataclass
class CreateUserSpec:
    firebase_uid: str
    phone_number: str
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    profil_image: Optional[str] = None


@dataclass
class FirebaseDecodedToken:
    user_id: str
    phone_number: str


@dataclass
class UserDomain:
    id: int
    firebase_id: str
    phone_number: str
    email: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None


@dataclass
class UpdateUserSpec:
    firebase_uid: str
    username: str
    name: str
    email: str
    profil_image: Optional[str] = None
