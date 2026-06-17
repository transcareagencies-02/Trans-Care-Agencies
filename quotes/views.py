from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.conf import settings
from core.email_utils import add_email_footer
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from products.models import QuoteRequest
from .forms import QuoteForm


def quote_home(request):
    if request.method == "POST":
        form = QuoteForm(request.POST, request.FILES)
        if form.is_valid():
            quote_request = form.save(commit=False)
            if request.user.is_authenticated:
                quote_request.user = request.user
            quote_request.save()

            try:
                EmailMessage(
                    subject="Quotation Request Received",
                    body=add_email_footer(
                        f"""
Dear {quote_request.user.username if quote_request.user else quote_request.institution_name},

Thank you for contacting Trans Care Agencies.

Your quotation request has been received successfully. Our sales team will review your requirements and provide a detailed quotation shortly.

Reference Number: {quote_request.id}

Regards,
Trans Care Sales & Quotations
"""
                    ),
                    from_email=settings.SALES_EMAIL,
                    to=[quote_request.email],
                ).send(fail_silently=True)
            except Exception:
                pass

            messages.success(request, "Your quote request has been submitted successfully.")
            return redirect("quote_success")
    else:
        form = QuoteForm()

    return render(request, "quotes/quote_request.html", {"form": form})


@staff_member_required
def update_quote_status(request, quote_id):
    quote_request = get_object_or_404(QuoteRequest, id=quote_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(QuoteRequest._meta.get_field("status").choices):
            quote_request.status = new_status

            uploaded_file = request.FILES.get("quotation_document")
            if uploaded_file:
                quote_request.quotation_document = uploaded_file

            admin_note = request.POST.get("admin_note", "").strip()
            if admin_note:
                quote_request.admin_note = admin_note

            if new_status == 'quoted':
                quote_request.quoted_at = timezone.now()
            elif quote_request.status != 'quoted':
                quote_request.quoted_at = None

            quote_request.save()
            messages.success(request, f"Quote request #{quote_request.id} status updated to {quote_request.get_status_display()}.")

    return redirect("admin_dashboard")


def quote_success(request):

    return render(
        request,
        "quotes/success.html"
    )