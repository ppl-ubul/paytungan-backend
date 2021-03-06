from datetime import datetime, timedelta
from django.utils import timezone
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock
from faker import Faker

from paytungan.app.auth.tests import TestAuthService
from paytungan.app.base.constants import BillStatus
from paytungan.app.common.exceptions import NotFoundException, ValidationErrorException
from paytungan.app.payment.services import PaymentService
from paytungan.app.payment.specs import (
    CreateInvoicePaymentSpec,
    CreatePaymentSpec,
    GetPaymentListSpec,
    InvoiceDomain,
    PaymentDomain,
    UpdateStatusSpec,
)
from paytungan.app.split_bill.tests import TestSplitBillService


class TestPaymentService(TestCase):
    def setUp(self) -> None:
        self.payment_accessor = MagicMock()
        self.xendit_provider = MagicMock()
        self.bill_accessor = MagicMock()
        self.split_bill_accessor = MagicMock()
        self.payment_service = PaymentService(
            payment_accessor=self.payment_accessor,
            xendit_provider=self.xendit_provider,
            bill_accessor=self.bill_accessor,
            split_bill_accessor=self.split_bill_accessor,
        )

    @staticmethod
    def _get_payment_dummy(seed: int, bill_id: Optional[int] = None):
        fake = Faker()
        Faker.seed(seed)

        time_now = timezone.now()
        return PaymentDomain(
            id=fake.pyint(),
            updated_at=time_now,
            created_at=time_now,
            bill_id=bill_id or fake.pyint(),
            expiry_date=time_now + timedelta(days=1),
        )

    @staticmethod
    def _get_invoice_dummy(seed: int):
        fake = Faker()
        Faker.seed(seed)

        time_now = timezone.now()
        return InvoiceDomain(
            id=fake.pystr(),
            description=fake.pystr(),
            invoice_url=fake.url(),
            expiry_date=time_now + timedelta(days=1),
            status=fake.pystr(),
            amount=fake.pyint(min_value=5000, max_value=10000),
        )

    def test_get_payment_success(self) -> None:
        seed = 3001
        fake_payment = self._get_payment_dummy(seed)
        fake_invoice = self._get_invoice_dummy(seed)

        self.payment_accessor.get.return_value = fake_payment
        self.xendit_provider.get_invoice.return_value = fake_invoice
        payment = self.payment_service.get_payment(fake_payment.id)

        self.assertEqual(payment.invoice, fake_invoice)

    def test_get_payment_empty(self) -> None:
        self.payment_accessor.get.return_value = None
        payment = self.payment_service.get_payment(1)

        self.assertEqual(payment, None)

    def test_get_payment_failed_invoice_empty(self) -> None:
        seed = 3002
        fake_payment = self._get_payment_dummy(seed)

        self.payment_accessor.get.return_value = fake_payment
        self.xendit_provider.get_invoice.return_value = None

        with self.assertRaises(ValidationErrorException):
            self.payment_service.get_payment(fake_payment.id)

    def test_get_payment_with_create_invoice(self) -> None:
        seed = 3003
        fake_payment = self._get_payment_dummy(seed)
        fake_payment.expiry_date -= timedelta(hours=25)
        fake_invoice = self._get_invoice_dummy(seed)
        fake_invoice2 = self._get_invoice_dummy(seed + 100)

        self.payment_accessor.get.return_value = fake_payment
        self.xendit_provider.get_invoice.return_value = fake_invoice
        self.xendit_provider.create_invoice.return_value = fake_invoice2

        payment = self.payment_service.get_payment(fake_payment.id)

        self.assertEqual(payment.invoice, fake_invoice2)

    def test_get_list_payment(self) -> None:
        spec = GetPaymentListSpec(
            user_id=1,
        )

        self.payment_service.get_payment_list(spec)

        self.assertTrue(1)

    def test_get_list_payment_by_status(self) -> None:
        spec = GetPaymentListSpec(
            status="PAID",
        )

        self.payment_service.get_payment_list(spec)

        self.assertTrue(1)

    def test_create_payment_success(self):
        seed = 3004
        user_dummy = TestAuthService._get_user_dummy(seed)
        bill_dummy = TestSplitBillService._get_bill_dummy(seed, user_id=user_dummy.id)
        payment_dummy = self._get_payment_dummy(seed, bill_dummy.id)
        invoice_dummy = self._get_invoice_dummy(seed)

        spec = CreatePaymentSpec(
            bill_id=1,
        )

        self.bill_accessor.get.return_value = bill_dummy
        self.payment_accessor.create.return_value = payment_dummy
        self.xendit_provider.create_invoice.return_value = invoice_dummy

        payment = self.payment_service.create_payment(spec, user_dummy)

        self.assertEqual(payment.reference_no, invoice_dummy.id)

    def test_create_payment_bill_not_found(self):
        spec = CreatePaymentSpec(
            bill_id=1,
        )

        self.bill_accessor.get.return_value = None
        with self.assertRaises(NotFoundException):
            self.payment_service.create_payment(spec, None)

    def test_create_payment_bill_and_user_not_match(self):
        seed = 3005
        user_dummy = TestAuthService._get_user_dummy(seed)
        bill_dummy = TestSplitBillService._get_bill_dummy(
            seed, user_id=user_dummy.id + 1
        )

        spec = CreatePaymentSpec(
            bill_id=1,
        )

        self.bill_accessor.get.return_value = bill_dummy
        with self.assertRaises(ValidationErrorException):
            self.payment_service.create_payment(spec, user_dummy)

    def test_create_payment_bill_paid(self):
        seed = 3006
        user_dummy = TestAuthService._get_user_dummy(seed)
        bill_dummy = TestSplitBillService._get_bill_dummy(seed, user_id=user_dummy.id)
        bill_dummy.status = BillStatus.PAID.value

        spec = CreatePaymentSpec(
            bill_id=1,
        )

        self.bill_accessor.get.return_value = bill_dummy
        with self.assertRaises(ValidationErrorException):
            self.payment_service.create_payment(spec, user_dummy)

    def test_payment_service_update_status(self):
        spec = UpdateStatusSpec(
            bill_id=1,
        )
        self.payment_service.update_status(spec)
        assert True

    def test_create_invoice_for_payment_success(self):
        seed = 3007
        fake_payment = self._get_payment_dummy(seed)
        fake_invoice = self._get_invoice_dummy(seed)

        self.payment_accessor.get.return_value = fake_payment
        self.xendit_provider.create_invoice.return_value = fake_invoice

        spec = CreateInvoicePaymentSpec(
            payment_id=fake_payment.id,
            payer_email=fake_invoice.payer_email,
            success_redirect_url=fake_invoice.success_redirect_url,
            failure_redirect_url=fake_invoice.failure_redirect_url,
        )

        result = self.payment_service.create_invoice_for_payment(spec)

        self.assertEqual(result.payment.invoice, fake_invoice)

    def test_create_invoice_for_payment_failed_payment_not_found(self):
        seed = 3007
        fake_payment = self._get_payment_dummy(seed)
        fake_invoice = self._get_invoice_dummy(seed)

        self.payment_accessor.get.return_value = None

        spec = CreateInvoicePaymentSpec(
            payment_id=fake_payment.id,
            payer_email=fake_invoice.payer_email,
            success_redirect_url=fake_invoice.success_redirect_url,
            failure_redirect_url=fake_invoice.failure_redirect_url,
        )

        with self.assertRaises(ValidationErrorException):
            self.payment_service.create_invoice_for_payment(spec)

    def test_get_payment_by_bill_id(self) -> None:
        self.payment_service.get_payment_by_bill_id(1)
        assert True
