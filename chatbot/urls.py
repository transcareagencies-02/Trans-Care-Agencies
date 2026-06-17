from django.urls import path
from . import views

urlpatterns = [

    path(
        "start/",
        views.start_chat,
        name="start_chat"
    ),

    path(
        "send/",
        views.send_message,
        name="send_message"
    ),

    path(
        "messages/<int:session_id>/",
        views.get_messages,
        name="get_messages"
    ),

    path(
        "live-chats/",
        views.live_chats,
        name="live_chats"
    ),

    path(
        "chat/<int:session_id>/",
        views.chat_detail,
        name="chat_detail"
    ),

    path(
        "reply/<int:session_id>/",
        views.staff_reply,
        name="staff_reply"
    ),

    path(
        "close/<int:session_id>/",
        views.close_chat,
        name="close_chat"
    ),

    path(
        "",
        views.customer_chat,
        name="chat_home"
    ),

]