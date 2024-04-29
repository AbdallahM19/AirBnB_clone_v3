#!/usr/bin/python3
"""Place"""
from api.v1.views import app_views
from flask import jsonify, request, abort, make_response
from models import storage
from models.city import City
from models.place import Place
from models.user import User
from models.amenity import Amenity
from models.state import State


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


@app_views.route(
    '/places_search',
    methods=['POST'],
    strict_slashes=False
)
def place_search_id():
    """search place"""
    data = request.get_json()
    if not data:
        return make_response(
            jsonify({"error": "Not a JSON"}), 400
        )
    states = data.get('states', None)
    cities = data.get('cities', None)
    amenities = data.get('amenities', None)
    if not states and not cities and not amenities:
        places = storage.all(Place).values()
        return jsonify([p.to_dict() for p in places])

    places = []
    if states:
        state_agrs = [
            storage.get(
                State, state_id
            ) for state_id in states
        ]
        for s in state_agrs:
            if s:
                for c in s.cities:
                    if c:
                        for p in c.places:
                            places.append(p)

    if cities:
        cities_args = [
            storage.get(
                City, city_id
            ) for city_id in cities
        ]
        for c in cities_args:
            if c:
                for p in c.places:
                    if p not in places:
                        places.append(p)

    if amenities:
        places = storage.all(
            Place
        ).values() if not places else places
        place_amenities = [
            storage.get(
                Amenity, amenity_id
            ) for amenity_id in amenities
        ]
        for p in places:
            if all(
                [
                    amenity_id in p.amenities
                    for amenity_id in place_amenities
                ]
            ):
                places.append(p)

    filtered_places = []
    for place in places:
        i = place.to_dict()
        i.pop('amenities', None)
        filtered_places.append(place)

    return jsonify(filtered_places)
