import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Annot, User
from config import Config, DBLogin
from datetime import datetime
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError
from videos import videos_bp
from batches import batches_bp
from models import Annot

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.register_blueprint(videos_bp, url_prefix="/api/video")
app.register_blueprint(batches_bp, url_prefix="/api/batches")

db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Flask is running"

@app.route('/add_annot', methods=['POST'])
def add_annot():
    data = request.get_json(force=True)
    if not User.query.filter_by(username=data["user"]).first():
        return jsonify({"error": "User not found"}), 403
    cmd = insert(Annot).values(
        sign=data['sign'],
        user=data["user"],
        label=data["label"],
        comments=data.get('comments', ""),
        time=datetime.fromtimestamp(data["time"] / 1000),
        video_path=os.path.basename(data["video_path"])
    ).on_duplicate_key_update(
        sign=data['sign'],
        label=data["label"],
        comments=data.get('comments', ""),
        time=datetime.fromtimestamp(data["time"] / 1000)
    )

    try:
        db.session.execute(cmd)
        db.session.commit()
        return jsonify({"message": "Added annotation"})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to add annotation"}), 500

@app.get("/annots")
def get_annots():
    data = request.args

    u = (data.get("username") or data.get("user") or "").strip()
    sign = (data.get("sign") or "").strip()
    if not u or not sign:
        return jsonify({"error": "user and sign required"}), 400

    fmt = (data.get("format") or "").strip().lower()
    batch_param = (data.get("batch") or "").strip()
    want_counts = (data.get("counts") or "").strip() in ("1", "true", "yes")

    q = db.session.query(Annot).filter_by(user=u, sign=sign)
    if batch_param:
        q = q.filter(Annot.batch == batch_param)

    q = q.order_by(Annot.video_path.asc(), Annot.time.asc())
    rows = q.all()

    latest = {}
    for r in rows:
        latest[r.video_path] = r

    if fmt != "summary":
        out = {
            vp: {
                "label": r.label,
                "comments": r.comments or "",
                "time": r.time.isoformat() if r.time else None,
            }
            for vp, r in latest.items()
        }
        return jsonify(out)

    items = [
        {
            "video": vp,
            "label": r.label,
            "time": r.time.isoformat() if r.time else None,
        }
        for vp, r in latest.items()
    ]
    items.sort(key=lambda x: x["video"])

    resp = {"items": items}
    if want_counts:
        counts = {}
        for it in items:
            counts[it["label"]] = counts.get(it["label"], 0) + 1
        resp["counts"] = counts

    return jsonify(resp)
    
@app.route('/check_user', methods=['POST'])
def check_user():
    from models import db, User
    data = request.json
    username = data.get("username")

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar()

    if user:
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
