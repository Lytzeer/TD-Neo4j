from flask import Blueprint, request, jsonify
from models.utilisateur import Utilisateur
from models.relations import Relations
from py2neo import Graph

users_bp = Blueprint('users', __name__)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
utilisateur = Utilisateur(graph)
relations = Relations(graph)


@users_bp.route('/users', methods=['GET'])
def get_users():
    users = graph.nodes.match("User")
    return jsonify([{"id": user.identity, "name": user["name"], "email": user["email"]} for user in users])

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    utilisateur.create_user(data['name'], data['email'])
    return jsonify({"message": "User created successfully"}), 201

@users_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = graph.nodes.get(user_id)
    if user and user["name"] and user.labels == {"User"}:
        return jsonify({"id": user.identity, "name": user["name"], "email": user["email"]})
    return jsonify({"error": "User not found"}), 404

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    user = graph.nodes.get(user_id)
    if user and user.labels == {"User"}:
        user["name"] = data.get("name", user["name"])
        user["email"] = data.get("email", user["email"])
        graph.push(user)
        return jsonify({"message": "User updated successfully"})
    return jsonify({"error": "User not found"}), 404

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = graph.nodes.get(user_id)
    if user and user.labels == {"User"}:
        graph.delete(user)
        return jsonify({"message": "User deleted successfully"})
    return jsonify({"error": "User not found"}), 404

@users_bp.route('/users/<int:user_id>/friends', methods=['GET'])
def get_user_friends(user_id):
    user = graph.nodes.get(user_id)
    if user and user.labels == {"User"}:
        friends = graph.match((user,), r_type="FRIENDS_WITH")
        return jsonify([{"id": friend.end_node.identity, "name": friend.end_node["name"]} for friend in friends])
    return jsonify({"error": "User not found"}), 404

@users_bp.route('/users/<int:user_id>/friends', methods=['POST'])
def add_friend(user_id):
    data = request.json
    friend_id = data['friend_id']
    friend_id = int(friend_id)
    user = graph.nodes.get(user_id)
    friend = graph.nodes.get(friend_id)
    if user and friend and user.labels == {"User"} and friend.labels == {"User"}:
        relations.create_friends_with_relationship(user, friend)
        return jsonify({"message": "Friend added successfully"})
    return jsonify({"error": "User or friend not found"}), 404

@users_bp.route('/users/<int:user_id>/friends/<int:friend_id>', methods=['DELETE'])
def remove_friend(user_id, friend_id):
    user = graph.nodes.get(user_id)
    friend = graph.nodes.get(friend_id)
    if user and friend and user.labels == {"User"} and friend.labels == {"User"}:
        rel = graph.match_one((user, friend), r_type="FRIENDS_WITH")
        if rel is not None:
            graph.separate(rel)
            return jsonify({"message": "Friend removed successfully"})
    return jsonify({"error": "User or friend not found"}), 404

@users_bp.route('/users/<int:user_id>/friends/<int:friend_id>', methods=['GET'])
def check_friendship(user_id, friend_id):
    user = graph.nodes.get(user_id)
    friend = graph.nodes.get(friend_id)
    if user and friend and user.labels == {"User"} and friend.labels == {"User"}:
        rel = graph.match_one((user, friend), r_type="FRIENDS_WITH")
        return jsonify({"are_friends": rel is not None})
    return jsonify({"error": "User or friend not found"}), 404

@users_bp.route('/users/<int:user_id>/mutual-friends/<int:other_id>', methods=['GET'])
def get_mutual_friends(user_id, other_id):
    user = graph.nodes.get(user_id)
    other = graph.nodes.get(other_id)
    if user and other and user.labels == {"User"} and other.labels == {"User"}:
        user_friends = set(friend.end_node for friend in graph.match((user,), r_type="FRIENDS_WITH"))
        other_friends = set(friend.end_node for friend in graph.match((other,), r_type="FRIENDS_WITH"))
        mutual_friends = user_friends & other_friends
        return jsonify([{"id": friend.identity, "name": friend["name"]} for friend in mutual_friends])
    return jsonify({"error": "User or other user not found"}), 404