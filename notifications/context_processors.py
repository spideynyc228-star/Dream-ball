def unread_notifications(request):
    if not request.user.is_authenticated:
        return {"unread_notification_count": 0, "notification_preview": []}
    notifications = request.user.notifications.order_by("-created_at")
    return {
        "unread_notification_count": notifications.filter(is_read=False).count(),
        "notification_preview": notifications[:4],
    }
