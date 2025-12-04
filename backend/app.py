from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- Inicialização ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petcard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Uploads
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})

login_manager = LoginManager()
login_manager.init_app(app)

# --- MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80))
    idade = db.Column(db.String(20))
    genero = db.Column(db.String(20))
    raca = db.Column(db.String(50))
    cor = db.Column(db.String(30))
    foto = db.Column(db.String(200))
    events = db.relationship('Event', backref='pet', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "idade": self.idade,
            "genero": self.genero,
            "raca": self.raca,
            "cor": self.cor,
            "foto": self.foto
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(200))
    data = db.Column(db.String(20), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "data": self.data,
            "pet_id": self.pet_id
        }

# --- LOGIN MANAGER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- CRIAR BANCO ---
with app.app_context():
    db.create_all()

# --- ROTAS DE USUÁRIO ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email já cadastrado"}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Usuário cadastrado com sucesso!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password, data.get('password')):
        login_user(user)
        return jsonify({"message": "Login realizado com sucesso!"})
    return jsonify({"error": "Email ou senha inválidos"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

# --- ROTAS DE UPLOAD ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- ROTAS DE PET ---
@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    return jsonify([p.to_dict() for p in pets])

@app.route('/pets', methods=['POST'])
def create_pet():
    nome = request.form.get('nome')
    idade = request.form.get('idade')
    genero = request.form.get('genero')
    raca = request.form.get('raca')
    cor = request.form.get('cor')

    foto = None
    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename:
            foto = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto))

    pet = Pet(nome=nome, idade=idade, genero=genero, raca=raca, cor=cor, foto=foto)
    db.session.add(pet)
    db.session.commit()
    return jsonify({"message": "Pet criado com sucesso!"}), 201

@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return jsonify(pet.to_dict())

@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    data = request.form or request.json

    pet.nome = data.get("nome", pet.nome)
    pet.idade = data.get("idade", pet.idade)
    pet.genero = data.get("genero", pet.genero)
    pet.raca = data.get("raca", pet.raca)
    pet.cor = data.get("cor", pet.cor)

    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename:
            pet.foto = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pet.foto))

    db.session.commit()
    return jsonify({'message': 'Pet atualizado com sucesso!'}), 200

@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deletado com sucesso!'}), 200

@app.route('/pets/<int:pet_id>/events', methods=['GET'])
def get_events(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    return jsonify([e.to_dict() for e in pet.events])

@app.route('/pets/<int:pet_id>/events', methods=['POST'])
def create_event(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    data = request.form or request.json

    nome = data.get("nome")
    descricao = data.get("descricao")
    data_evento = data.get("data")

    if not nome or not data_evento:
        return jsonify({"error": "Nome e data são obrigatórios"}), 400

    event = Event(nome=nome, descricao=descricao, data=data_evento, pet=pet)
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Evento criado com sucesso!"}), 201

@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Pet.query.session.query(Event).get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Evento deletado com sucesso!"}), 200

@app.route('/session', methods=['GET'])
def check_session():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "user": current_user.email}), 200
    return jsonify({"authenticated": False}), 401


if __name__ == "__main__":
    app.run(debug=True)
