from flask import Flask
from py2neo import Graph

from routes.users import users_bp
from routes.comments import posts_bp
from routes.posts import comments_bp

app = Flask(__name__)

graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(posts_bp, url_prefix="/posts")
app.register_blueprint(comments_bp, url_prefix="/comments")

if __name__ == '__main__':
    app.run(debug=True)
