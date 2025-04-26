from flask import Blueprint, request, jsonify
from models.commentaire import Commentaire
from models.relations import Relations
from py2neo import Graph, Node
from datetime import datetime

posts_bp = Blueprint('posts', __name__)
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
commentaire = Commentaire(graph)
relations = Relations(graph)

@posts_bp.route('/comments', methods=['GET'])
def get_all_comments():
    comments = graph.nodes.match("Comment")
    return jsonify([
        {"id": comment.identity, "content": comment["content"]}
        for comment in comments
    ])

@posts_bp.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment_by_id(comment_id):
    comment = graph.nodes.get(comment_id)
    if comment and comment.labels == {"Comment"}:
        return jsonify({"id": comment.identity, "content": comment["content"]})
    return jsonify({"error": "Comment not found"}), 404

@posts_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def create_comment(post_id):
    data = request.json
    user_id = data['user_id']
    content = data['content']

    user = graph.nodes.get(user_id)
    post = graph.nodes.get(post_id)

    if user and post and post.labels == {"Post"} and user.labels == {"User"}:
        comment_node = Node("Comment", content=content, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        graph.create(comment_node)
        commentaire
        relations.create_created_relationship(user, comment_node)
        relations.create_has_comment_relationship(post, comment_node)
        return jsonify({"message": "Comment added successfully"}), 201

    return jsonify({"error": "User or post not found"}), 404

@posts_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_comments_for_post(post_id):
    post = graph.nodes.get(post_id)
    if post and post.labels == {"Post"}:
        comments = graph.match((post,), r_type="HAS_COMMENT")
        return jsonify([
            {"id": comment.end_node.identity, "content": comment.end_node["content"]}
            for comment in comments
        ])
    return jsonify({"error": "Post not found"}), 404

@posts_bp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.json
    comment = graph.nodes.get(comment_id)
    if comment and comment.labels == {"Comment"}:
        comment["content"] = data.get("content", comment["content"])
        graph.push(comment)
        return jsonify({"message": "Comment updated successfully"})
    return jsonify({"error": "Comment not found"}), 404

@posts_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = graph.nodes.get(comment_id)
    if comment and comment.labels == {"Comment"}:
        graph.delete(comment)
        return jsonify({"message": "Comment deleted successfully"})
    return jsonify({"error": "Comment not found"}), 404

@posts_bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment_from_post(post_id, comment_id):
    post = graph.nodes.get(post_id)
    comment = graph.nodes.get(comment_id)
    if post and comment and post.labels == {"Post"} and comment.labels == {"Comment"}:
        rel = graph.match_one((post, comment), r_type="HAS_COMMENT")
        if rel is not None:
            graph.delete(comment)
            return jsonify({"message": "Comment deleted successfully"})
    return jsonify({"error": "Post or comment not found"}), 404

@posts_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    data = request.json
    user_id = data['user_id']
    user = graph.nodes.get(user_id)
    comment = graph.nodes.get(comment_id)
    if user and comment and comment.labels == {"Comment"} and user.labels == {"User"}:
        relations.create_likes_relationship(user, comment)
        return jsonify({"message": "Comment liked successfully"})

@posts_bp.route('/comments/<int:comment_id>/like', methods=['DELETE'])
def unlike_comment(comment_id):
    data = request.json
    user_id = data['user_id']
    user = graph.nodes.get(user_id)
    comment = graph.nodes.get(comment_id)
    if user and comment and comment.labels == {"Comment"} and user.labels == {"User"}:
        print("User and comment found")
        rel = graph.match_one((user, comment), r_type="LIKES")
        print(rel is not None)
        if rel is not None:
            print("Relationship found")
            graph.separate(rel)
            return jsonify({"message": "Comment unliked successfully"})
    return jsonify({"error": "User or comment not found"}), 404