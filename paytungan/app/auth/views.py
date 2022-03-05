from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from paytungan.app.auth.services import (
    AuthService,
    UserServices,
)
from paytungan.app.common.decorators import api_exception
from paytungan.app.base.headers import AUTH_HEADERS, DEFAULT_HEADERS
from paytungan.app.base.serializers import AuthHeaderRequest

from .serializers import (
    GetUserRequest,
    GetUserResponse,
    CreateUserRequest,
    CreateUserResponse,
    LoginRequest,
    LoginResponse,
    UpdateUserRequest,
    UpdateUserResponse,
)
from .specs import CreateUserSpec, UpdateUserSpec
from paytungan.app.di import injector

user_service = injector.get(UserServices)
auth_service = injector.get(AuthService)


class UserViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        url_path="get",
        methods=["get"],
    )
    @swagger_auto_schema(
        query_serializer=GetUserRequest(),
        responses={200: GetUserResponse()},
    )
    @api_exception
    def get_user(self, request: Request) -> Response:
        """
        Get single user object
        by user id or user name
        """
        serializer = GetUserRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = user_service.get(data["user_id"])
        return Response(GetUserResponse({"data": user}).data)

    @action(
        detail=False,
        url_path="create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=CreateUserRequest(),
        responses={200: CreateUserResponse()},
    )
    @api_exception
    def create_user(self, request: Request) -> Response:
        """
        Create user
        """
        header_serializer = AuthHeaderRequest(data=request.headers)
        header_serializer.is_valid(raise_exception=True)
        serializer = CreateUserRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = CreateUserSpec(
            firebase_uid=data["username"],
            phone_number=data["phone_number"],
            username=data["username"],
            name=data["name"],
            email=data["email"],
            profil_image=data["profil_image"],
        )
        user = user_service.create_user(spec)
        return Response(CreateUserResponse({"data": user}).data)

    @action(
        detail=False,
        url_path="update",
        methods=["post"],
    )
    @swagger_auto_schema(
        request_body=UpdateUserRequest(),
        responses={200: UpdateUserResponse()},
    )
    @api_exception
    def update_user(self, request: Request) -> Response:
        """
        Update User
        """
        serializer = UpdateUserRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = UpdateUserSpec(
            firebase_uid=data["firebase_uid"],
            username=data["username"],
            name=data["name"],
            profil_image=data["profil_image"],
        )
        user = user_service.update_user(spec)
        return Response(UpdateUserResponse({"data": user}).data)


class AuthViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        url_path="login",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=DEFAULT_HEADERS,
        request_body=LoginRequest(),
        responses={200: LoginResponse()},
    )
    @api_exception
    def login(self, request: Request) -> Response:
        """
        Authentication Login and Register
        """
        serializer = LoginRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = auth_service.login(data["token"])
        return Response(LoginResponse({"data": user}).data)
