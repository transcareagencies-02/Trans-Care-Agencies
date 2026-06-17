import json

from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.email_utils import add_email_footer

from .models import Payment
from .utils import generate_receipt, reduce_stock_for_order

from orders.models import Order
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone


# =========================
# DOWNLOAD RECEIPT
# =========================

@login_required
def download_receipt(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user
    )

    # CHECK RECEIPT EXISTS
    if not payment.receipt:

        messages.error(
            request,
            "Receipt not available yet."
        )

        return redirect("admin_dashboard")

    return FileResponse(
        payment.receipt.open(),
        as_attachment=True
    )


# =========================
# =========================

@login_required
def pay_order(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return redirect(
        'initiate_payment',
        order.id
    )


# =========================
# INITIATE PAYMENT
# =========================

@login_required
def initiate_payment(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    phone = request.user.phone

    if phone.startswith("0"):
        phone = "254" + phone[1:]

    from .mpesa import stk_push
    response = stk_push(
        phone=phone,
        amount=order.total_amount,
        account_reference=f"ORDER-{order.id}"
    )

    print("STK RESPONSE:", response)

    if response.get("ResponseCode") == "0":

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "amount": order.total_amount,
                "method": "mpesa",
                "status": "pending",
                "checkout_request_id": response.get(
                    "CheckoutRequestID"
                )
            }
        )

        if not created:
            payment.checkout_request_id = response.get(
                "CheckoutRequestID"
            )
            payment.status = "pending"
            payment.save()

        return redirect(
            "payment_status",
            payment.id
        )

    messages.error(
        request,
        response.get(
            "errorMessage",
            "STK Push failed"
        )
    )

    return redirect("admin_dashboard")

# =========================
# CHECK PAYMENT STATUS
# =========================

@login_required
def check_payment_status(request, checkout_id):

    payment = Payment.objects.filter(
        checkout_request_id=checkout_id
    ).first()

    if not payment:

        return JsonResponse({
            "status": "pending"
        })

    return JsonResponse({

        "status": payment.status,
        "transaction_id": payment.transaction_id

    })

# =========================
# PAYMENT STATUS PAGE
# =========================

@login_required
def payment_status(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user
    )

    return render(
        request,
        "payments/payment_status.html",
        {
            "payment": payment
        }
    )

# =========================
# MPESA CALLBACK
# =========================

@csrf_exempt
def mpesa_callback(request):

    try:

        data = json.loads(request.body)
        
        print("CALLBACK DATA:", data)

        result = data.get(
            'Body',
            {}
        ).get(
            'stkCallback',
            {}
        )

        checkout_id = result.get('CheckoutRequestID')

        result_code = result.get('ResultCode')

        if not checkout_id:

            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Missing CheckoutRequestID"
            })

        payment = Payment.objects.filter(
            checkout_request_id=checkout_id
        ).select_related('order').first()

        if not payment:

            print("❌ Payment not found:", checkout_id)

            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Payment not found"
            })

        # PREVENT DUPLICATES
        if payment.status == "completed":

            return JsonResponse({
                "ResultCode": 0,
                "ResultDesc": "Already processed"
            })

        # SUCCESSFUL PAYMENT
        if result_code == 0:

            metadata = result.get(
                'CallbackMetadata',
                {}
            ).get(
                'Item',
                []
            )

            def get_value(name):

                for item in metadata:

                    if item.get('Name') == name:
                        return item.get('Value')

                return None

            amount = get_value('Amount')

            mpesa_code = get_value(
                'MpesaReceiptNumber'
            )

            # UPDATE PAYMENT
            payment.status = 'completed'
            payment.transaction_id = mpesa_code
            payment.amount = amount

            payment.save()

            receipt_file = generate_receipt(payment)

            if receipt_file:
                from django.core.files import File
                import os

                full_path = os.path.join(settings.MEDIA_ROOT, receipt_file)

                with open(full_path, 'rb') as f:
                    payment.receipt.save(
                        f"receipt_{payment.id}.pdf",
                        File(f),
                        save=False
                    )

                payment.save()
            # UPDATE ORDER
            order = payment.order

            if order:

                order.status = 'confirmed'
                order.is_paid = True

                order.save()

                try:
                    reduce_stock_for_order(order)
                except ValueError:
                    pass

            # SEND EMAIL
            try:

                email = EmailMessage(

                    subject=f"Official Receipt – Order #{order.id}",

                    body=add_email_footer(
                        f"""
Dear {order.user.username},

Your official receipt has been generated and is attached to this email.

Receipt Number: {payment.id}
Order Number: #{order.id}

Please keep this document for your records.

Regards,
Trans Care Finance Department
"""
                    ),
                    from_email=settings.RECEIPTS_EMAIL,
                    to=[order.user.email]

                )

                if payment.receipt:
                    email.attach_file(
                        payment.receipt.path
                    )

                email.send()

            except Exception as e:

                print("📧 Email error:", e)

        else:

            payment.status = 'failed'
            payment.save()

    except Exception as e:

        print("🔥 M-Pesa Callback Error:", e)

    return JsonResponse({
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    })

@login_required
def bank_transfer(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "user": request.user,
            "amount": order.total_amount,
            "method": "bank",
            "status": "pending",
        }
    )

    if request.method == "POST":

        payment.bank_reference = (request.POST.get("reference") or "").strip()
        proof_file = request.FILES.get("proof")

        if not payment.bank_reference:
            messages.error(request, "Please enter the bank transaction reference.")
            return render(request, "payments/bank_transfer.html", {"payment": payment})

        if not proof_file:
            messages.error(request, "Please upload proof of payment before submitting.")
            return render(request, "payments/bank_transfer.html", {"payment": payment})

        payment.proof_of_payment = proof_file

        payment.save()

        messages.success(
            request,
            "Bank transfer submitted successfully."
        )

        return redirect("admin_dashboard")

    return render(
        request,
        "payments/bank_transfer.html",
        {
            "payment": payment
        }
    )

@staff_member_required
def bank_verifications(request):

    payments = Payment.objects.filter(
        method='bank',
        status='pending'
    )

    return render(
        request,
        "admin/bank_verifications.html",
        {
            "payments": payments
        }
    )

@staff_member_required
def approve_bank_payment(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    payment.status = "completed"

    payment.verified_by = request.user

    payment.verified_at = timezone.now()

    payment.transaction_id = payment.bank_reference

    payment.save()

    order = payment.order

    order.status = "confirmed"
    order.is_paid = True

    order.save()

    try:
        reduce_stock_for_order(order)
    except ValueError:
        messages.error(request, "Stock update could not be completed because one or more items are out of stock.")
        return redirect("bank_verifications")

    receipt = generate_receipt(payment)

    payment.receipt = receipt

    payment.save()

    try:
        EmailMessage(
            subject=f"Payment Received – Order #{order.id}",
            body=add_email_footer(
                f"""
Dear {order.user.username},

We are pleased to confirm that we have received your payment.

Transaction Reference: {payment.transaction_id or payment.bank_reference or 'N/A'}
Amount Paid: KES {payment.amount}
Order Number: #{order.id}

Thank you for choosing Trans Care Agencies.

Regards,
Trans Care Billing & Payments
"""
            ),
            from_email=settings.RECEIPTS_EMAIL,
            to=[order.user.email],
        ).send(fail_silently=True)
    except Exception:
        pass

    messages.success(
        request,
        "Payment approved successfully."
    )

    return redirect(
        "bank_verifications"
    )


@staff_member_required
def reject_bank_payment(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    payment.status = "failed"
    payment.verified_by = request.user
    payment.verified_at = timezone.now()
    payment.save()

    order = payment.order
    if order:
        order.status = "pending"
        order.is_paid = False
        order.save()

    messages.success(
        request,
        f"Payment for order #{payment.order.id} was rejected successfully."
    )

    return redirect("bank_verifications")


def bank_payment_view(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        method="bank"
    )

    if request.method == "POST":

        payment.bank_reference = (request.POST.get("reference") or "").strip()
        proof_file = request.FILES.get("proof")

        if not payment.bank_reference:
            messages.error(request, "Please enter the bank transaction reference that is on your payment slip/cheque.")
            return render(request, "payments/bank_transfer.html", {"payment": payment})

        if not proof_file:
            messages.error(request, "Please upload proof of slip/cheque payment before submitting.")
            return render(request, "payments/bank_transfer.html", {"payment": payment})

        payment.proof_of_payment = proof_file

        payment.save()

        messages.success(
            request,
            "Bank transfer submitted successfully."
        )

        return redirect("admin_dashboard")

    return render(
        request,
        "payments/bank_transfer.html",
        {"payment": payment}
    )