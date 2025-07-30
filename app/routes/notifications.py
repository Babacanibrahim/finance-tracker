from flask import Blueprint, session, redirect, url_for, request, jsonify

notifications_bp = Blueprint("notifications", __name__)

# Bildirimlere okundu bilgisi
@notifications_bp.route("/mark_notification_read/<int:budget_id>/<int:category_id>")
def mark_notification_read(budget_id, category_id):
    notif_id = f"{budget_id}-{category_id}"

    # Okunan bildirimleri session'a ekleme
    read = session.get("read_notifications", [])
    if notif_id not in read:
        read.append(notif_id)
        session["read_notifications"] = read

    return redirect(url_for("limits.view_limit", id=budget_id))

# Bildirimlerin hepsini okuma
@notifications_bp.route("/mark_all_read", methods=["POST"])
def mark_all_read():
    data = request.get_json() or {}

    notif_ids = data.get("notif_ids", [])
    read = session.get("read_notifications", [])

    for nid in notif_ids:
        if nid not in read:
            read.append(nid)

    session["read_notifications"] = read

    return jsonify({"status": "success"})