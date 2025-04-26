from flask import Blueprint, request, jsonify
from models.post import Post
from models.relations import Relations
from py2neo import Graph, Node

comments_bp = Blueprint('comments', __name__)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
post = Post(graph)
relations = Relations(graph)

@comments_bp.route('/posts', methods=['GET'])
def get_posts():
    posts = graph.nodes.match("Post")
    return jsonify([{"id": post.identity, "title": post["title"], "content": post["content"]} for post in posts])

@comments_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post_by_id(post_id):
    post = graph.nodes.get(post_id)
    if post and post.labels == {"Post"}:
        return jsonify({"id": post.identity, "title": post["title"], "content": post["content"]})
    return jsonify({"error": "Post not found"}), 404

@comments_bp.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user = graph.nodes.get(user_id)
    if user and user.labels == {"User"}:
        posts = graph.match((user,), r_type="CREATED")
        return jsonify([{"id": post.end_node.identity, "title": post.end_node["title"], "content": post.end_node["content"]} for post in posts])
    return jsonify({"error": "User not found"}), 404

@comments_bp.route('/users/<int:user_id>/posts', methods=['POST'])
def create_post(user_id):
    data = request.json
    title = data['title']
    content = data['content']
    user = graph.nodes.get(user_id)
    if user and user.labels == {"User"}:
        post_node = Node("Post", title=title, content=content)
        graph.create(post_node)
        relations.create_created_relationship(user, post_node)
        return jsonify({"message": "Post created successfully"}), 201
    return jsonify({"error": "User not found"}), 404

@comments_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = graph.nodes.get(post_id)
    if post and post.labels == {"Post"}:
        graph.delete(post)
        return jsonify({"message": "Post deleted successfully"})
    return jsonify({"error": "Post not found"}), 404

@comments_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.json
    post = graph.nodes.get(post_id)
    if post and post.labels == {"Post"}:
        post["title"] = data.get("title", post["title"])
        post["content"] = data.get("content", post["content"])
        graph.push(post)
        return jsonify({"message": "Post updated successfully"})
    return jsonify({"error": "Post not found"}), 404

@comments_bp.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    data = request.json
    user_id = data['user_id']
    user_id = int(user_id)
    user = graph.nodes.get(user_id)
    post = graph.nodes.get(post_id)
    if user and post and post.labels == {"Post"} and user.labels == {"User"}:
        relations.create_likes_relationship(user, post)
        return jsonify({"message": "Post liked successfully"})
    return jsonify({"error": "User or post not found"}), 404

@comments_bp.route('/posts/<int:post_id>/like', methods=['DELETE'])
def unlike_post(post_id):
    data = request.json
    user_id = data['user_id']
    user_id = int(user_id)
    user = graph.nodes.get(user_id)
    post = graph.nodes.get(post_id)

    if user and post and post.labels == {"Post"} and user.labels == {"User"}:
        rel = graph.match_one((user, post), r_type="LIKES")
        if rel is not None:
            graph.separate(rel)
            return jsonify({"message": "Post unliked successfully"})
    return jsonify({"error": "User or post not found"}), 404