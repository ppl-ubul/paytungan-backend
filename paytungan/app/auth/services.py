from typing import List, Optional
from .models import User
from injector import inject

from .interfaces import IFirebaseProvider, IUserAccessor
from .specs import (
    FirebaseDecodedToken,
    GetUserListSpec,
    CreateUserSpec,
    UpdateUserSpec,
)


class UserServices:
    @inject
    def __init__(self, user_accessor: IUserAccessor) -> None:
        self.user_accessor = user_accessor

    def get(self, user_id: int) -> Optional[User]:
        return self.user_accessor.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.user_accessor.get_by_username(username)

    def get_by_firebase_uid(self, firebase_uid: int) -> Optional[User]:
        return self.user_accessor.get_by_firebase_uid(firebase_uid)

    def get_list(self, spec: GetUserListSpec) -> List[User]:
        return self.user_accessor.get_list(spec)

    def create_user(self, spec: CreateUserSpec) -> Optional[User]:
        user = self.user_accessor.create(spec)
        return user

    def update_user(self, spec: UpdateUserSpec) -> Optional[User]:
        user = self.user_accessor.update(spec)
        return user


class AuthService:
    @inject
    def __init__(
        self,
        user_accessor: IUserAccessor,
        firebase_provider: IFirebaseProvider,
    ) -> None:
        self.user_accessor = user_accessor
        self.firebase_provider = firebase_provider

    def get_user_from_token(self, token: str) -> Optional[User]:
        decoded_token = self.firebase_provider.decode_token(token)

        return self.user_accessor.get_by_firebase_uid(
            firebase_uid=decoded_token.user_id
        )

    def login(self, token: str) -> Optional[User]:
        decoded_token = self.firebase_provider.decode_token(token)

        user = self.user_accessor.get_by_firebase_uid(decoded_token.user_id)

        if user:
            return user

        return self.user_accessor.create(
            CreateUserSpec(
                firebase_uid=decoded_token.user_id,
                phone_number=decoded_token.phone_number,
            )
        )

    def decode_token(self, token: str) -> Optional[FirebaseDecodedToken]:
        return self.firebase_provider.decode_token(token)
