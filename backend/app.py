import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from . import db
from .models import Pet

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Rota para servir imagens
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rota: listar pets
@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    pets_data = [
        {
            'id': p.id,
            'nome': p.nome,
            'idade': p.idade,
            'genero': p.genero,
            'raca': p.raca,
            'cor': p.cor,
            'foto': p.foto
        } for p in pets
    ]
    return jsonify(pets_data)

# Rota: criar pet
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
        if file.filename != '':
            foto = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto))

    pet = Pet(nome=nome, idade=idade, genero=genero, raca=raca, cor=cor, foto=foto)
    db.session.add(pet)
    db.session.commit()

    return jsonify({'message': 'Pet criado com sucesso!'}), 201

# Rota: visualizar pet
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    pet_data = {
        'id': pet.id,
        'nome': pet.nome,
        'idade': pet.idade,
        'genero': pet.genero,
        'raca': pet.raca,
        'cor': pet.cor,
        'foto': pet.foto
    }
    return jsonify(pet_data)

# Rota: editar pet
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    data = request.form or request.json

    pet.nome = data.get('nome', pet.nome)
    pet.idade = data.get('idade', pet.idade)
    pet.genero = data.get('genero', pet.genero)
    pet.raca = data.get('raca', pet.raca)
    pet.cor = data.get('cor', pet.cor)

    if 'foto' in request.files:
        file = request.files['foto']
        if file.filename != '':
            foto = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto))
            pet.foto = foto

    db.session.commit()
    return jsonify({'message': 'Pet atualizado com sucesso!'})

# Rota: deletar pet
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': 'Pet deletado com sucesso!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
