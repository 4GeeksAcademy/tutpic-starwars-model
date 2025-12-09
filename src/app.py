"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, favorite_planets, favorite_characters
from sqlalchemy import insert, delete
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)




@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized = list(map(lambda x: User.serialize(x), users))

    return jsonify({"users":serialized}), 200



@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"msg":"No se recivieron datos"}),400
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not(email and username and password):
        return jsonify({"msg":"No se recivieron los datos pertinentes"}),400
    
    new_user = User(
        email=email,
        username=username,
        password=password,
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    return {
        "msg": "Usuario creado con exito",
        "user": new_user.serialize()
    },201



@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg":"No se encontro un usuario con ese id"}),404
    
    return jsonify({"msg":"Usuario encontrado con éxito","user":user.serialize()}),200



@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if user == None:
        return jsonify({"msg":"No existe un usuario con ese id"}), 400
  
    serialize = user.serialize_favs()
    return jsonify({"favorite_planets":serialize["favorite_planets"],"favorite_characters":serialize["favorite_characters"]}), 200
    


@app.route("/users/<int:user_id>/planets/<int:plan_id>",methods=["POST"])
def add_favorite_planet(user_id,plan_id):

    check_user = User.query.get(user_id)
    check_planet = Planet.query.get(plan_id)

    if not(check_user and check_planet):
        return jsonify({"msg":"El usuario o planeta no existen"}),404
    
    new_table = insert(favorite_planets).values(user_id=user_id,planet_id=plan_id)
    
    db.session.execute(new_table)
    db.session.commit()

    return {"msg":"Planeta favorito añadido con éxito"},201

@app.route("/users/<int:user_id>/planets/<int:plan_id>",methods=["DELETE"])
def delete_favorite_planet(user_id,plan_id):

    check_user = User.query.get(user_id)
    check_planet = Planet.query.get(plan_id)

    if not(check_user and check_planet):
        return jsonify({"msg":"El usuario o planeta no existen"}),404
    
    for planet in check_user.favorite_planets:
        if planet.id == plan_id:
            del_planet = planet
            break
    
    if not del_planet:
        return jsonify({"msg":"Este planeta no es favorito de este usuario"}),400

    
    new_table = delete(favorite_planets).where(favorite_planets.c.user_id==user_id and favorite_planets.c.planet_id==plan_id)

    db.session.execute(new_table)
    db.session.commit()

    return jsonify({"msg":"Planeta favorito borrado con éxito"}),200

@app.route("/users/<int:user_id>/people/<int:char_id>",methods=["POST"])
def add_favorite_character(user_id,char_id):

    check_user = User.query.get(user_id)
    check_character = Character.query.get(char_id)

    if not(check_user and check_character):
        return jsonify({"msg":"El usuario o personaje no existen"}),404
    
    new_table = insert(favorite_characters).values(user_id=user_id,character_id=char_id)
    
    db.session.execute(new_table)
    db.session.commit()

    return {"msg":"Personaje favorito añadido con éxito"},201

@app.route("/users/<int:user_id>/people/<int:char_id>",methods=["DELETE"])
def delete_favorite_character(user_id,char_id):

    check_user = User.query.get(user_id)
    check_char = Character.query.get(char_id)

    if not(check_user and check_char):
        return jsonify({"msg":"El usuario o personaje no existen"}),404
    
    for character in check_user.favorite_characters:
        if character.id == char_id:
            del_char = character
            break
    
    if not del_char:
        return jsonify({"msg":"Este personaje no es favorito de este usuario"}),400

    
    new_table = delete(favorite_characters).where(favorite_characters.c.user_id==user_id and favorite_characters.c.character_id==char_id)

    db.session.execute(new_table)
    db.session.commit()

    return jsonify({"msg":"Personaje favorito borrado con éxito"}),200

@app.route("/people", methods=["GET"])
def get_characters():
    characters = Character.query.all()
    serialized = list(map(lambda x: x.serialize(), characters))

    return jsonify(serialized), 200



@app.route("/people", methods=["POST"])
def create_character():
    data = request.get_json()

    if not data:
        return jsonify({"msg":"No se recivieron datos"}),400
    
    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    weight = data.get("weight")
    skin_color = data.get("skin_color")
    hair_color = data.get("hair_color")
    eye_color = data.get("eye_color")

    if not(name and age and gender and weight and skin_color and hair_color and eye_color):
        return jsonify({"msg":"No se recivieron los datos pertinentes"}),400

    new_character = Character(
        name=name,
        age=age,
        gender=gender,
        weight=weight,
        skin_color=skin_color,
        hair_color=hair_color,
        eye_color=eye_color
    )        

    db.session.add(new_character)
    db.session.commit()

    return jsonify({"msg":"Personaje creado con éxito","character":new_character.serialize()}),201



@app.route("/people/<int:char_id>", methods=["GET"])
def get_character(char_id):
    character = Character.query.get(char_id)
    if character == None:
        return jsonify({"msg": "No existe un personaje con ese id"}), 404
    return jsonify(character.serialize()), 200



@app.route("/planets", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    serialized = list(map(lambda x: x.serialize(), planets))

    return jsonify(serialized), 200



@app.route("/planets", methods=["POST"])
def create_planet():

    data = request.get_json()

    if not data:
        return jsonify({"msg":"No se recivieron datos"}),400

    gravity = data.get("gravity")
    population = data.get("population")
    diameter = data.get("diameter")
    name = data.get("name")
    climate = data.get("climate")
    terrain = data.get("terrain")
    rotation_period = data.get("rotation_period")

    if not(gravity and population and diameter and name and climate and terrain and rotation_period):
        return jsonify({"msg":"No se recivieron los datos pertinentes"}),400
    
    new_planet = Planet(
        gravity=gravity,
        population=population,
        diameter=diameter,
        name=name,
        climate=climate,
        terrain=terrain,
        rotation_period=rotation_period
    )
    db.session.add(new_planet)
    db.session.commit()

    return jsonify({"msg":"Planeta creado con éxito","planet":new_planet.serialize()}),201

@app.route("/planets/<int:plan_id>", methods=["GET"])
def get_planet(plan_id):
    planet = Planet.query.get(plan_id)
    if planet == None:
        return jsonify({"msg": "No existe un planeta con ese id"}), 404
    return jsonify(planet.serialize()), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
