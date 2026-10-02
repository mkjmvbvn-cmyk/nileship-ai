from flask import Flask, request, jsonify
from pathlib import Path
from datetime import datetime, timezone
import json

app = Flask(__name__)

DATA_FILE = Path(__file__).with_name("shipments.json")
with DATA_FILE.open("r", encoding="utf-8") as f:
    DATA = json.load(f)

SHIPMENTS = {item["shipment_id"]: item for item in DATA.get("shipments", [])}
ACTION_LOG = []

def now():
    return datetime.now(timezone.utc).isoformat()

def json_error(message, status=400):
    return jsonify({"ok": False, "error": message}), status

@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "NileShip AI demo backend",
        "shipments": len(SHIPMENTS)
    })

@app.post("/track_shipment")
def track_shipment():
    body = request.get_json(silent=True) or {}
    shipment_id = str(body.get("shipment_id", "")).strip().upper()

    if not shipment_id:
        return json_error("shipment_id is required")

    shipment = SHIPMENTS.get(shipment_id)
    if not shipment:
        return jsonify({
            "ok": False,
            "found": False,
            "message": "الشحنة غير موجودة في بيانات التجربة."
        }), 404

    return jsonify({
        "ok": True,
        "found": True,
        "shipment": shipment
    })

@app.post("/reschedule_delivery")
def reschedule_delivery():
    body = request.get_json(silent=True) or {}
    shipment_id = str(body.get("shipment_id", "")).strip().upper()
    requested_day = str(body.get("requested_day", "")).strip()

    if not shipment_id or not requested_day:
        return json_error("shipment_id and requested_day are required")

    if shipment_id not in SHIPMENTS:
        return jsonify({"ok": False, "message": "الشحنة غير موجودة في بيانات التجربة."}), 404

    action = {
        "action": "reschedule_delivery",
        "shipment_id": shipment_id,
        "requested_day": requested_day,
        "created_at": now(),
        "demo": True
    }
    ACTION_LOG.append(action)

    return jsonify({
        "ok": True,
        "demo": True,
        "message": "تم تسجيل طلب إعادة الجدولة للتجربة.",
        "request": action
    })

@app.post("/update_address")
def update_address():
    body = request.get_json(silent=True) or {}
    shipment_id = str(body.get("shipment_id", "")).strip().upper()
    address_details = str(body.get("address_details", "")).strip()

    if not shipment_id or not address_details:
        return json_error("shipment_id and address_details are required")

    if shipment_id not in SHIPMENTS:
        return jsonify({"ok": False, "message": "الشحنة غير موجودة في بيانات التجربة."}), 404

    action = {
        "action": "update_address",
        "shipment_id": shipment_id,
        "address_details": address_details,
        "created_at": now(),
        "demo": True
    }
    ACTION_LOG.append(action)

    return jsonify({
        "ok": True,
        "demo": True,
        "message": "تم تسجيل تفاصيل العنوان للتجربة.",
        "request": action
    })

@app.post("/contact_courier")
def contact_courier():
    body = request.get_json(silent=True) or {}
    shipment_id = str(body.get("shipment_id", "")).strip().upper()

    if not shipment_id:
        return json_error("shipment_id is required")

    shipment = SHIPMENTS.get(shipment_id)
    if not shipment:
        return jsonify({"ok": False, "message": "الشحنة غير موجودة في بيانات التجربة."}), 404

    action = {
        "action": "contact_courier",
        "shipment_id": shipment_id,
        "courier": shipment.get("courier"),
        "created_at": now(),
        "demo": True
    }
    ACTION_LOG.append(action)

    return jsonify({
        "ok": True,
        "demo": True,
        "message": "تم تسجيل طلب التواصل مع المندوب للتجربة.",
        "courier": shipment.get("courier"),
        "request": action
    })

@app.post("/human_handoff")
def human_handoff():
    body = request.get_json(silent=True) or {}
    shipment_id = str(body.get("shipment_id", "")).strip().upper()
    reason = str(body.get("reason", "")).strip()

    if not reason:
        return json_error("reason is required")

    action = {
        "action": "human_handoff",
        "shipment_id": shipment_id or None,
        "reason": reason,
        "created_at": now(),
        "demo": True
    }
    ACTION_LOG.append(action)

    return jsonify({
        "ok": True,
        "demo": True,
        "message": "تم تسجيل طلب التحويل لموظف خدمة العملاء في النسخة التجريبية.",
        "request": action
    })

@app.get("/demo_actions")
def demo_actions():
    return jsonify({"ok": True, "actions": ACTION_LOG})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
