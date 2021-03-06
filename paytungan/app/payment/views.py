from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.db import transaction

from paytungan.app.common.decorators import api_exception
from paytungan.app.base.headers import AUTH_HEADERS
from paytungan.app.auth.utils import user_auth, firebase_auth
from paytungan.app.auth.specs import UserDomain, FirebaseDecodedToken
from paytungan.app.common.utils import ObjectMapperUtil

from .specs import (
    CreatePaymentSpec,
    CreatePayoutSpec,
    UpdateStatusSpec,
    GetPaymentListSpec,
)
from .serializers import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    CreatePayoutRequest,
    CreatePayoutResponse,
    GetPaymentResponse,
    GetPaymentRequest,
    GetPayoutRequest,
    GetPayoutResponse,
    UpdateStatusRequest,
    UpdateStatusResponse,
    GetPaymentByBillIdRequest,
    GetPaymentByBillIdResponse,
    GetPaymentListRequest,
    GetPaymentListResponse,
)
from .services import (
    PaymentService,
)
from paytungan.app.di import injector

payment_service = injector.get(PaymentService)


class PaymentViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        url_path="get",
        methods=["get"],
    )
    @swagger_auto_schema(
        query_serializer=GetPaymentRequest(),
        responses={200: GetPaymentResponse()},
    )
    @api_exception
    def get_payment(self, request: Request) -> Response:
        """
        Get single payment object by id
        """
        serializer = GetPaymentRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        payment = payment_service.get_payment(data["id"])
        return Response(GetPaymentResponse({"data": payment}).data)

    @action(
        detail=False,
        url_path="create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=CreatePaymentRequest(),
        responses={200: CreatePaymentResponse()},
    )
    @transaction.atomic
    @api_exception
    @user_auth
    def create_payment(self, request: Request, user: UserDomain) -> Response:
        serializer = CreatePaymentRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = CreatePaymentSpec(
            bill_id=data["bill_id"],
            success_redirect_url=data["success_redirect_url"],
            failure_redirect_url=data["failure_redirect_url"],
        )
        user = payment_service.create_payment(spec, user)
        return Response(CreatePaymentResponse({"data": user}).data)

    @action(
        detail=False,
        url_path="update/paid",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=UpdateStatusRequest(),
        responses={200: UpdateStatusResponse()},
    )
    @transaction.atomic
    @api_exception
    @firebase_auth
    def update_user(self, request: Request, cred: FirebaseDecodedToken) -> Response:
        """
        Update Status
        """
        serializer = UpdateStatusRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = UpdateStatusSpec(
            bill_id=data["bill_id"],
        )
        payment = payment_service.update_status(spec)
        return Response(UpdateStatusResponse({"data": payment}).data)

    @action(
        detail=False,
        url_path="get/bill_id",
        methods=["get"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        query_serializer=GetPaymentByBillIdRequest(),
        responses={200: GetPaymentByBillIdResponse()},
    )
    @api_exception
    @firebase_auth
    def get_split_bill_list(
        self, request: Request, cred: FirebaseDecodedToken
    ) -> Response:
        """
        Get payment by bill id
        """
        serializer = GetPaymentByBillIdRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        payment = payment_service.get_payment_by_bill_id(data["bill_id"])
        return Response(GetPaymentByBillIdResponse({"data": payment}).data)

    @action(
        detail=False,
        url_path="payout/get",
        methods=["get"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        query_serializer=GetPayoutRequest(),
        responses={200: GetPayoutResponse()},
    )
    @api_exception
    @firebase_auth
    def get_payout(self, request: Request, cred: FirebaseDecodedToken) -> Response:
        """
        Get payout by split bill id
        """
        serializer = GetPayoutRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        payment = payment_service.get_payout(data["split_bill_id"])
        return Response(GetPayoutResponse({"data": payment}).data)

    @action(
        detail=False,
        url_path="payout/create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=CreatePayoutRequest(),
        responses={200: CreatePayoutResponse()},
    )
    @api_exception
    @firebase_auth
    def create_payout(self, request: Request, cred: FirebaseDecodedToken) -> Response:
        """
        Create payout of given split_bill
        """
        serializer = CreatePayoutRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = ObjectMapperUtil.map(data, CreatePayoutSpec)
        payout = payment_service.create_payout(spec)
        return Response(GetPayoutResponse({"data": payout}).data)

    @action(
        detail=False,
        url_path="payout/get-or-create",
        methods=["post"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        request_body=GetPayoutRequest(),
        responses={200: GetPayoutResponse()},
    )
    @api_exception
    @firebase_auth
    def get_or_create_payout(
        self, request: Request, cred: FirebaseDecodedToken
    ) -> Response:
        """
        Create payout of given split_bill
        """
        serializer = GetPayoutRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = ObjectMapperUtil.map(data, CreatePayoutSpec)
        payout = payment_service.get_or_create_payout(spec)
        return Response(GetPayoutResponse({"data": payout}).data)

    @action(
        detail=False,
        url_path="list/get",
        methods=["get"],
    )
    @swagger_auto_schema(
        manual_parameters=AUTH_HEADERS,
        query_serializer=GetPaymentListRequest(),
        responses={200: GetPaymentListResponse()},
    )
    @api_exception
    @firebase_auth
    def get_payment_list(
        self, request: Request, cred: FirebaseDecodedToken
    ) -> Response:
        """
        Get list payment object
        """
        serializer = GetPaymentListRequest(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        spec = ObjectMapperUtil.map(data, GetPaymentListSpec)
        payments = payment_service.get_payment_list(spec)
        return Response(GetPaymentListResponse({"data": payments}).data)
