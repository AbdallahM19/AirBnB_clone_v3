#!/usr/bin/python3
"""Place"""
from api.v1.views import app_views
from flask import jsonify, request, abort, make_response
from models import storage
from models.city import City
from models.place import Place
from models.user import User


@app_views.route(
    '/cities/<city_id>/places',
    methods=['GET'],
    strict_slashes=False
)
def get_places(city_id):
    """get all places"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    all_places = [i.to_dict() for i in city.places]
    return jsonify(all_places)


@app_views.route(
    '/places/<place_id>',
    methods=['GET'],
    strict_slashes=False
)
def get_place(place_id):
    """get place from id"""
    i = storage.get(Place, place_id)
    if i is None:
        abort(404)
    return jsonify(i.to_dict())


@app_views.route(
    '/places/<place_id>',
    methods=['DELETE'],
    strict_slashes=False
)
def delete_place(place_id):
    """delete place from id"""
    i = storage.get(Place, place_id)
    if i is None:
        abort(404)
    storage.delete(i)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route(
    '/cities/<city_id>/places',
    methods=['POST'],
    strict_slashes=False
)
def create_place(city_id):
    """create place"""
    place = request.get_json()
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not place:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    if 'user_id' not in place:
        return make_response(jsonify({"error": "Missing user_id"}), 400)
    place['city_id'] = city_id
    user = storage.get(User, place['user_id'])
    if user is None:
        abort(404)
    if 'name' not in place:
        return make_response(jsonify({"error": "Missing name"}), 400)
    i = Place(**place)
    i.save()
    return make_response(jsonify(i.to_dict()), 201)


@app_views.route(
    '/places/<place_id>',
    methods=['PUT'],
    strict_slashes=False
)
def update_place(place_id):
    """update place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Not a JSON"}), 400
        )
    for k, v in data.items():
        if k not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, k, v)
    storage.save()
    return jsonify(place.to_dict())
