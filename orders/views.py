from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.urls import reverse
from payments.mpesa import stk_push
from payments.models import Payment
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from django.conf import settings
from core.email_utils import add_email_footer
import csv
import os
from datetime import datetime


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        item.quantity = qty
        item.save()

    return redirect('cart_view')


@login_required
def checkout_view(request):

    cart, _ = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.select_related(
        'product'
    )

    for item in items:
        item.subtotal = (
            item.quantity *
            item.product.price
        )

    total = sum(
        item.subtotal
        for item in items
    )

    if request.method == "POST":

        # TERMS
        if not request.POST.get("accept_terms"):

            return render(
                request,
                "checkout/checkout.html",
                {
                    "items": items,
                    "total": total,
                    "error": "You must accept Terms and Policies."
                }
            )

        payment_method = request.POST.get(
            "payment_method"
        )

        # ==========================
        # CREATE ORDER
        # ==========================

        phone = request.POST.get("phone") or request.user.phone or ""
        customer_kra_pin = getattr(request.user, "kra_pin", "") or ""

        for cart_item in items:
            if cart_item.quantity > cart_item.product.stock:
                return render(
                    request,
                    "checkout/checkout.html",
                    {
                        "items": items,
                        "total": total,
                        "error": f"Only {cart_item.product.stock} unit(s) available for {cart_item.product.name}."
                    }
                )

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status="pending",
            is_paid=False,
            phone=phone,
            customer_kra_pin=customer_kra_pin,
            delivery_address=getattr(request.user, "postal_address", "") or ""
        )

        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        EmailMessage(
            subject=f"Order Confirmation – Order #{order.id}",
            body=add_email_footer(
                f"""
Dear {request.user.username},

Thank you for your order with Trans Care Agencies.

We have successfully received your order and our team is preparing it for processing.

Order Number: #{order.id}
Order Value: KES {total:.2f}

You will receive further updates as your order progresses.

Regards,
Trans Care Order Management
"""
            ),
            from_email=settings.ORDERS_EMAIL,
            to=[request.user.email],
        ).send(fail_silently=True)

        cart.items.all().delete()

        # ==========================
        # MPESA PAYMENT
        # ==========================

        if payment_method == "mpesa":

            phone = request.POST.get("phone")

            if not phone:

                return render(
                    request,
                    "checkout/checkout.html",
                    {
                        "items": items,
                        "total": total,
                        "error": "Phone number required."
                    }
                )

            response = stk_push(
                phone=phone,
                amount=int(total),
                account_reference=f"ORDER-{order.id}"
            )

            print("STK RESPONSE:", response)

            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=total,
                method="mpesa",
                status="pending",
                checkout_request_id=response.get(
                    "CheckoutRequestID"
                )
            )

            return redirect(
                "payment_status",
                payment.id
            )

        # ==========================
        # BANK TRANSFER
        # ==========================

        elif payment_method == "bank":

            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=total,
                method="bank",
                status="pending"
            )

            return redirect(
                "bank_payment",
                payment.id
            )

    return render(
        request,
        "checkout/checkout.html",
        {
            "items": items,
            "total": total
        }
    )

@login_required
def payment_status(request, payment_id):

    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user
    )

    return render(request, "checkout/payment_status.html", {
        "payment": payment
    })


def get_cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
    else:
        count = 0
    return JsonResponse({'count': count})


# =========================
# INVOICE GENERATION
# =========================

@login_required
def generate_invoice(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    PAGE_WIDTH, PAGE_HEIGHT = A4
    left_margin = right_margin = 40
    top_margin = bottom_margin = 40

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    styles = getSampleStyleSheet()
    styles['Title'].fontSize = 18
    styles['Title'].leading = 20
    styles['Heading1'].fontSize = 12
    styles['Heading1'].leading = 14
    styles['Heading2'].fontSize = 9
    styles['Heading2'].leading = 11
    styles['Normal'].fontSize = 9
    styles['Normal'].leading = 11

    elements = []

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=110, height=42))
    else:
        elements.append(Paragraph(settings.COMPANY_NAME, styles['Title']))

    elements.append(Spacer(1, 6))

    company_block = Paragraph(
        f"<b>{settings.COMPANY_NAME}</b><br/>"
        f"{settings.COMPANY_ADDRESS}<br/>"
        f"{settings.COMPANY_PO_BOX}<br/>"
        f"Tel: {settings.COMPANY_PHONE}<br/>"
        f"Email: {settings.COMPANY_EMAIL}<br/>"
        f"KRA PIN: {settings.COMPANY_KRA_PIN}",
        styles['Normal'],
    )
    elements.append(company_block)
    elements.append(Spacer(1, 18))

    title = Paragraph("INVOICE", styles['Title'])
    elements.append(title)

    is_paid = bool(order.is_paid or order.status.lower() in {"paid", "completed"})
    status_text = "PAID" if is_paid else "UNPAID"
    status_color = colors.HexColor("#15803D") if is_paid else colors.HexColor("#DC2626")

    status_style = ParagraphStyle(
        "StatusBadge",
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=status_color,
        spaceAfter=6,
    )
    elements.append(Paragraph(status_text, status_style))
    elements.append(Spacer(1, 6))

    invoice_meta = [
        ["Invoice No", f"INV-{order.id:05d}"],
        ["Order No", str(order.id)],
        ["Date", datetime.now().strftime("%d-%m-%Y")],
        ["Status", order.status.title()],
    ]

    meta_table = Table(
        invoice_meta,
        colWidths=[140, 330],
        repeatRows=0,
    )
    meta_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 18))

    customer_name = order.user.get_full_name() or order.user.username
    customer_data = [
        ["Bill To", customer_name],
        ["Email", order.user.email or "N/A"],
        ["Phone", order.phone or "N/A"],
        ["KRA PIN", getattr(order, 'customer_kra_pin', None) or getattr(order.user, 'kra_pin', None) or 'N/A'],
        ["Delivery Address", order.delivery_address or 'N/A'],
    ]

    customer_table = Table(customer_data, colWidths=[140, 330])
    customer_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(Paragraph("Customer Details", styles['Heading1']))
    elements.append(Spacer(1, 6))
    elements.append(customer_table)
    elements.append(Spacer(1, 18))

    payment_instructions = [
        ["Payment Method", "Bank Transfer / M-Pesa"],
        ["Bank Transfer", "Bank: KCB Bank\nA/C Name: Trans Care Agencies Ltd\nA/C No: 1234567890\nReference: ORDER-" + str(order.id)],
        ["M-Pesa BuyGoods", "Till: 4127016\nAccount Name: Mose Muhoma\nUse the order number as your reference where possible."],
    ]

    payment_table = Table(payment_instructions, colWidths=[140, 330])
    payment_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(Paragraph("Payment Details", styles['Heading1']))
    elements.append(Spacer(1, 6))
    elements.append(payment_table)
    elements.append(Spacer(1, 18))

    items = [["Item", "Qty", "Unit Price", "Total"]]
    for item in order.items.select_related('product').all():
        items.append([
            item.product.name,
            str(item.quantity),
            f"KES {float(item.price):,.2f}",
            f"KES {float(item.get_total_price()):,.2f}",
        ])

    items_table = Table(items, colWidths=[250, 60, 80, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(Paragraph("Order Summary", styles['Heading1']))
    elements.append(Spacer(1, 6))
    elements.append(items_table)

    subtotal = float(order.total_amount)
    grand_total = subtotal

    totals = [
        ["Subtotal", f"KES {grand_total:,.2f}"],
        ["Total Due", f"KES {grand_total:,.2f}"],
    ]

    totals_table = Table(totals, colWidths=[250, 220])
    totals_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#E0F2FE')),
    ]))
    elements.append(Spacer(1, 12))
    elements.append(totals_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "Thank you for choosing Trans Care Agencies. Please keep this invoice for your records.",
        styles['Normal'],
    ))

    doc.build(elements)

    try:
        EmailMessage(
            subject=f"Invoice Ready for Order #{order.id}",
            body=(
                f"Hello {order.user.username},\n\n"
                f"Your invoice for order #{order.id} is ready to download.\n\n"
                f"Download it here: {request.build_absolute_uri(reverse('generate_invoice', args=[order.id]))}"
            ),
            from_email=settings.ORDERS_EMAIL,
            to=[order.user.email],
        ).send(fail_silently=True)
    except Exception:
        pass

    return response


# =========================
# EXPORT SALES
# =========================

def export_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Amount', 'Status', 'Date'])

    orders = Order.objects.all()

    for order in orders:
        writer.writerow([
            order.id,
            order.user.username if order.user else "Guest",
            order.total_amount,
            order.status,
            order.created_at
        ])

    return response