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
    data = request.json
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

if __name__ == '__main__':
    app.run(debug=True)
