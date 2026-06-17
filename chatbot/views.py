from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from .models import ChatSession, ChatMessage

import json


# ====================================
# CUSTOMER START CHAT
# ====================================

@login_required
def start_chat(request):

    session, created = ChatSession.objects.get_or_create(
        customer=request.user,
        status="open"
    )

    return JsonResponse({
        "session_id": session.id
    })


# ====================================
# SEND MESSAGE
# ====================================

@login_required
@csrf_exempt
def send_message(request):

    if request.method == "POST":

        data = json.loads(request.body)

        session_id = data.get("session_id")
        message = data.get("message")

        session = get_object_or_404(
            ChatSession,
            id=session_id
        )

        ChatMessage.objects.create(
            session=session,
            sender=request.user,
            message=message
        )

        return JsonResponse({
            "success": True
        })

    return JsonResponse({
        "success": False
    })


# ====================================
# GET CHAT MESSAGES
# ====================================

@login_required
def get_messages(request, session_id):

    session = get_object_or_404(
        ChatSession,
        id=session_id
    )

    messages = ChatMessage.objects.filter(
        session=session
    ).order_by("created_at")

    data = []

    for msg in messages:

        data.append({

            "sender": msg.sender.username,

            "message": msg.message,

            "time": msg.created_at.strftime(
                "%d %b %Y %H:%M"
            )

        })

    return JsonResponse(data, safe=False)


# ====================================
# STAFF CHAT LIST
# ====================================

@login_required
def live_chats(request):

    if not request.user.is_staff:
        return redirect("/")

    sessions = ChatSession.objects.select_related(
        "customer"
    ).order_by("-created_at")

    return render(
        request,
        "chatbot/live_chats.html",
        {
            "sessions": sessions
        }
    )


# ====================================
# OPEN CHAT
# ====================================

@login_required
def chat_detail(request, session_id):

    if not request.user.is_staff:
        return redirect("/")

    session = get_object_or_404(
        ChatSession,
        id=session_id
    )

    messages = ChatMessage.objects.filter(
        session=session
    ).order_by("created_at")

    return render(
        request,
        "chatbot/chat_detail.html",
        {
            "session": session,
            "messages": messages
        }
    )


# ====================================
# STAFF REPLY
# ====================================

@login_required
def staff_reply(request, session_id):

    if not request.user.is_staff:
        return redirect("/")

    if request.method == "POST":

        session = get_object_or_404(
            ChatSession,
            id=session_id
        )

        message = request.POST.get("message")

        ChatMessage.objects.create(
            session=session,
            sender=request.user,
            message=message
        )

        return redirect('chat_detail', session_id=session_id)

    return redirect("/")


# ====================================
# CLOSE CHAT
# ====================================

@login_required
def close_chat(request, session_id):

    session = get_object_or_404(
        ChatSession,
        id=session_id
    )

    session.status = "closed"
    session.save()

    return JsonResponse({
        "success": True
    })

@login_required
def customer_chat(request):

    return render(
        request,
        "chatbot/customer_chat.html"
    )