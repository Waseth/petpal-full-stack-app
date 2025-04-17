from flask import Blueprint, request, jsonify
from database import db
from models import Pet, Adopter
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

routes_bp = Blueprint('routes', __name__)

# ---------- PET ROUTES ----------

@routes_bp.route('/pets', methods=['GET'])
def get_pets():
    # Retrieve query parameters for search and filter
    name = request.args.get('name', '')  # Search by name (default empty string for no search)
    breed = request.args.get('breed', '')  # Search by breed
    age_min = request.args.get('age_min', type=int)  # Filter by minimum age
    age_max = request.args.get('age_max', type=int)  # Filter by maximum age
    adopted = request.args.get('adopted', type=bool)  # Filter by adoption status (True or False)

    query = Pet.query

    # Apply search by name or breed if provided
    if name:
        query = query.filter(Pet.name.ilike(f'%{name}%'))
    if breed:
        query = query.filter(Pet.breed.ilike(f'%{breed}%'))

    # Apply filters for age range if provided
    if age_min is not None:
        query = query.filter(Pet.age >= age_min)
    if age_max is not None:
        query = query.filter(Pet.age <= age_max)

    # Apply filter for adoption status if provided
    if adopted is not None:
        query = query.filter(Pet.adopted == adopted)

    pets = query.all()

    return jsonify([{
        'id': pet.id,
        'name': pet.name,
        'age': pet.age,
        'breed': pet.breed,
        'adopted': pet.adopted
    } for pet in pets])

@routes_bp.route('/pets', methods=['POST'])
@jwt_required()
def add_pet():
    data = request.get_json()
    if not data.get("name") or not data.get("age") or not data.get("breed"):
        return jsonify({"error": "Missing required fields"}), 400

    pet = Pet(name=data['name'], age=data['age'], breed=data['breed'])

    try:
        db.session.add(pet)
        db.session.commit()
        return jsonify({'message': 'Pet added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/adopt', methods=['POST'])
@jwt_required()
def adopt_pet():
    data = request.get_json()
    pet_id = data.get("pet_id")
    adopter_id = data.get("adopter_id")

    pet = Pet.query.get(pet_id)
    adopter = Adopter.query.get(adopter_id)

    if not pet or not adopter:
        return jsonify({"message": "Pet or adopter not found"}), 404
    if pet.adopted:
        return jsonify({"message": "Pet already adopted"}), 400

    pet.adopted = True
    pet.adopter_id = adopter.id

    try:
        db.session.commit()
        return jsonify({"message": f"{pet.name} successfully adopted by {adopter.name}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/undo_adoption/<int:pet_id>', methods=['PATCH'])
@jwt_required()
def undo_adoption(pet_id):
    pet = Pet.query.get(pet_id)

    if not pet:
        return jsonify({"message": "Pet not found"}), 404
    if not pet.adopted:
        return jsonify({"message": "Pet is not adopted"}), 400

    pet.adopted = False
    pet.adopter_id = None

    try:
        db.session.commit()
        return jsonify({"message": f"Adoption for {pet.name} has been undone."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ---------- DELETE PET ROUTE FOR ADOPTER ----------

@routes_bp.route('/pets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_pet(id):
    # Get the logged-in user's identity (adopter)
    current_adopter_id = get_jwt_identity()

    # Get the pet object by ID
    pet = Pet.query.get(id)

    # Check if the pet exists
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    # Check if the logged-in adopter is the adopter of the pet
    if pet.adopter_id != current_adopter_id:
        return jsonify({'error': 'You are not authorized to delete this pet'}), 403

    # Delete the pet if the adopter matches
    try:
        db.session.delete(pet)
        db.session.commit()
        return jsonify({'message': f'Pet with id {id} has been deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ---------- ADOPTER ROUTES ----------

@routes_bp.route('/adopters', methods=['GET'])
@jwt_required()
def get_adopters():
    adopters = Adopter.query.all()
    return jsonify([{
        'id': adopter.id,
        'name': adopter.name,
        'email': adopter.email,
        'phone': adopter.phone
    } for adopter in adopters])

@routes_bp.route('/adopters', methods=['POST'])
@jwt_required()
def add_adopter():
    data = request.get_json()

    if not data.get("name") or not data.get("email") or not data.get("phone"):
        return jsonify({"error": "Missing required fields"}), 400

    adopter = Adopter(name=data['name'], email=data['email'], phone=data['phone'])

    try:
        db.session.add(adopter)
        db.session.commit()
        return jsonify({'message': 'Adopter added successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@routes_bp.route('/adopters/<int:adopter_id>/pets', methods=['GET'])
@jwt_required()
def get_pets_by_adopter(adopter_id):
    adopter = Adopter.query.get(adopter_id)
    if not adopter:
        return jsonify({"message": "Adopter not found"}), 404

    pets = Pet.query.filter_by(adopter_id=adopter.id).all()

    return jsonify([{
        'id': pet.id,
        'name': pet.name,
        'age': pet.age,
        'breed': pet.breed,
        'adopted': pet.adopted
    } for pet in pets])
