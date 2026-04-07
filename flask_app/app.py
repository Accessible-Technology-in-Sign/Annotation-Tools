import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Annot
from config import Config, DBLogin
from datetime import datetime
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DBLogin.USER}:{DBLogin.PSWD}@localhost/labels'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Flask is running"

@app.route('/add_annot', methods=['POST'])
def add_annot():
    from models import User, Annot
    data = request.json
    
    if not db.session.execute(db.select(User).filter_by(username=data["user"])).scalar():
        return jsonify({"error": "User not found"}), 403
        
    cmd = insert(Annot).values(
        sign=data['sign'],
        batch=data.get('batch', 'unknown'),
        user=data["user"],
        label=data["label"],
        comments=data.get('comments', ""),
        time=datetime.fromtimestamp(data["time"] / 1000),
        video_path=os.path.basename(data["video_path"])
    ).on_duplicate_key_update(
        sign=data['sign'],
        batch=data.get('batch', 'unknown'),
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

@app.route('/get_progress/<username>/<batch>', methods=['GET'])
def get_progress(username, batch):
    from models import Annot
    
    # Query for unique signs annotated by this user in this batch
    query = db.select(Annot.sign).filter_by(user=username, batch=batch).distinct()
    completed_signs = db.session.execute(query).scalars().all()
    
    return jsonify({
        "completed_count": len(completed_signs),
        "completed_signs": completed_signs
    })
    
@app.route('/check_user', methods=['POST'])
def check_user():
    from models import User
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
    app.run(debug=True)
