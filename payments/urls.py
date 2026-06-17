from django.urls import path
from . import views

urlpatterns = [

    path(
        "receipt/<int:payment_id>/",
        views.download_receipt,
        name="download_receipt"
    ),

    path(
        "pay/<int:order_id>/",
        views.pay_order,
        name="pay_order"
    ),

    path(
        "initiate/<int:order_id>/",
        views.initiate_payment,
        name="initiate_payment"
    ),

    path(
        "status/<int:payment_id>/",
        views.payment_status,
        name="payment_status"
    ),

    path(
        "check/<str:checkout_id>/",
        views.check_payment_status,
        name="check_payment_status"
    ),

    path(
        "callback/",
        views.mpesa_callback,
        name="mpesa_callback"
    ),

    path(
        "bank-transfer/<int:order_id>/",
        views.bank_transfer,
        name="bank_transfer"
    ),

    path(
        "bank-verifications/",
        views.bank_verifications,
        name="bank_verifications"
    ),

    path(
        "approve-bank-payment/<int:payment_id>/",
        views.approve_bank_payment,
        name="approve_bank_payment"
    ),

    path(
        "reject-bank-payment/<int:payment_id>/",
        views.reject_bank_payment,
        name="reject_bank_payment"
    ),

    path(
        "bank/<int:payment_id>/",
        views.bank_payment_view,
        name="bank_payment"
    ),

]