from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from django.conf import settings

import os
from datetime import datetime


def reduce_stock_for_order(order):
    for item in order.items.select_related('product').all():
        if item.quantity > item.product.stock:
            raise ValueError(f"Not enough stock for {item.product.name}")

        item.product.stock -= item.quantity
        item.product.save(update_fields=['stock'])

    return True


def generate_receipt(payment):

    file_name = f"receipt_{payment.id}.pdf"

    file_path = os.path.join(
        settings.MEDIA_ROOT,
        "receipts",
        file_name
    )

    os.makedirs(
        os.path.dirname(file_path),
        exist_ok=True
    )

    # page size and margins tuned to fit one page
    PAGE_WIDTH, PAGE_HEIGHT = A4
    left_margin = right_margin = 30
    top_margin = bottom_margin = 30

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    usable_width = PAGE_WIDTH - left_margin - right_margin

    styles = getSampleStyleSheet()

    # reduce default font sizes to help fit content on one page
    styles['Title'].fontSize = 11
    styles['Title'].leading = 13
    styles['Heading1'].fontSize = 11
    styles['Heading1'].leading = 13
    styles['Heading2'].fontSize = 9
    styles['Heading2'].leading = 11
    styles['Normal'].fontSize = 7.5
    styles['Normal'].leading = 9
    styles['Italic'].fontSize = 7.5

    elements = []

    order = payment.order

    # ==================================
    # COMPANY LOGO
    # ==================================

    logo_path = os.path.join(
        settings.MEDIA_ROOT,
        "logo.png"
    )

    if os.path.exists(logo_path):

        logo = Image(
            logo_path,
            width=100,
            height=40
        )

        elements.append(logo)

    elements.append(Spacer(1, 6))

    # ==================================
    # COMPANY HEADER
    # ==================================

    company_header = f"""
    <b>{settings.COMPANY_NAME}</b><br/>
    {settings.COMPANY_ADDRESS}<br/>
    {settings.COMPANY_PO_BOX}<br/>
    Tel: {settings.COMPANY_PHONE}<br/>
    Email: {settings.COMPANY_EMAIL}<br/>
    KRA PIN: {settings.COMPANY_KRA_PIN}
    """

    elements.append(
        Paragraph(
            company_header,
            styles['Title']
        )
    )

    elements.append(Spacer(1, 10))

    # ==================================
    # RECEIPT TITLE
    # ==================================

    elements.append(
        Paragraph(
            f"OFFICIAL PAYMENT RECEIPT",
            styles['Heading1']
        )
    )

    elements.append(Spacer(1, 6))

    # ==================================
    # CUSTOMER INFO
    # ==================================

    customer_name = (
        order.user.get_full_name()
        if order.user.get_full_name()
        else order.user.username
    )

    customer_kra = (
        getattr(order, "customer_kra_pin", None)
        or getattr(order.user, "kra_pin", None)
        or "N/A"
    )

    phone = (
        getattr(order, "phone", None)
        or getattr(order.user, "phone", None)
        or "N/A"
    )

    customer_data = [

        ["Customer Name", customer_name],

        ["Email", order.user.email],

        ["Phone", phone],

        ["Customer KRA PIN", customer_kra]

    ]

    customer_table = Table(
        customer_data,
        colWidths=[usable_width * 0.35, usable_width * 0.65]
    )

    customer_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.black),

        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")

    ]))

    elements.append(
        Paragraph(
            "CUSTOMER INFORMATION",
            styles['Heading2']
        )
    )

    elements.append(customer_table)

    elements.append(Spacer(1, 10))

    # ==================================
    # RECEIPT DETAILS
    # ==================================

    receipt_data = [

        ["Receipt No", f"RCT-{payment.id:05d}"],

        ["Order No", str(order.id)],

        ["Transaction Code",
         payment.transaction_id or "N/A"],

        ["Payment Method",
         payment.method.upper()],

        ["Payment Date",
         payment.payment_date.strftime("%d-%m-%Y %H:%M")],

        ["Status",
         payment.status.upper()]

    ]

    receipt_table = Table(
        receipt_data,
        colWidths=[usable_width * 0.35, usable_width * 0.65]
    )

    receipt_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),0.5,colors.black),

        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")

    ]))

    elements.append(
        Paragraph(
            "PAYMENT DETAILS",
            styles['Heading2']
        )
    )

    elements.append(receipt_table)

    elements.append(Spacer(1, 10))

    # ==================================
    # ORDER ITEMS
    # ==================================

    item_rows = [[
        "Item Name",
        "Qty",
        "Unit Price",
        "Total"
    ]]

    order_items = order.items.select_related('product').all()

    for item in order_items:
        item_rows.append([
            item.product.name,
            str(item.quantity),
            f"KES {float(item.price):,.2f}",
            f"KES {float(item.get_total_price()):,.2f}"
        ])

    item_rows.append(["", "", "ORDER TOTAL", f"KES {float(payment.amount):,.2f}"])

    item_table = Table(
        item_rows,
        colWidths=[usable_width * 0.45, usable_width * 0.13, usable_width * 0.21, usable_width * 0.21]
    )

    item_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 7)
    ]))

    elements.append(
        Paragraph(
            "ORDER ITEMS",
            styles['Heading2']
        )
    )

    elements.append(item_table)

    elements.append(Spacer(1, 10))

    # ==================================
    # VAT CALCULATIONS
    # ==================================

    total = float(payment.amount)

    subtotal = total / 1.16

    vat = total - subtotal

    vat_data = [

        ["Subtotal", f"KES {subtotal:,.2f}"],

        ["VAT (16%)", f"KES {vat:,.2f}"],

        ["TOTAL PAID", f"KES {total:,.2f}"]

    ]

    vat_table = Table(
        vat_data,
        colWidths=[usable_width * 0.5, usable_width * 0.5]
    )

    vat_table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,2),(-1,2),
         colors.lightgreen),

        ("FONTNAME",(0,2),(-1,2),
         "Helvetica-Bold")

    ]))

    elements.append(
        Paragraph(
            "VAT SUMMARY",
            styles['Heading2']
        )
    )

    elements.append(vat_table)

    elements.append(Spacer(1, 12))

    # ==================================
    # VERIFIED STAMP
    # ==================================

    stamp_path = os.path.join(
        settings.MEDIA_ROOT,
        "stamp.png"
    )

    if os.path.exists(stamp_path):

        stamp = Image(
            stamp_path,
            width=80,
            height=80
        )

        elements.append(stamp)

    else:

        elements.append(
            Paragraph(
                "<b>✓ VERIFIED PAYMENT</b>",
                styles['Heading2']
            )
        )

    elements.append(Spacer(1, 10))

    # ==================================
    # FOOTER
    # ==================================

    elements.append(
        Paragraph(
            """
            Thank you for doing business with
            Trans Care Agencies Ltd.
            """,
            styles['Normal']
        )
    )

    elements.append(
        Paragraph(
            """
            This receipt was automatically
            generated by the Trans Care
            Ecommerce System.
            """,
            styles['Italic']
        )
    )

    elements.append(
        Paragraph(
            f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles['Normal']
        )
    )

    doc.build(elements)

    return f"receipts/{file_name}"