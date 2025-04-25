from py2neo import Graph, Node, Relationship
from datetime import datetime

class Utilisateur:
    def __init__(self, graph: Graph):
        self.graph = graph

    def create_user(self, name: str, email: str):
        user_node = Node("User", name=name, email=email, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.graph.create(user_node)

class Post:
    def __init__(self, graph: Graph):
        self.graph = graph

    def create_post(self, title: str, content: str):
        post_node = Node("Post", title=title, content=content, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.graph.create(post_node)

class Commentaire:
    def __init__(self, graph: Graph):
        self.graph = graph

    def create_comment(self, content: str):
        comment_node = Node("Comment", content=content, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.graph.create(comment_node)

class Relations:
    def __init__(self, graph: Graph):
        self.graph = graph

    def create_created_relationship(self, user_node: Node, target_node: Node):
        created_rel = Relationship(user_node, "CREATED", target_node)
        self.graph.create(created_rel)

    def create_has_comment_relationship(self, post_node: Node, comment_node: Node):
        has_comment_rel = Relationship(post_node, "HAS_COMMENT", comment_node)
        self.graph.create(has_comment_rel)

    def create_friends_with_relationship(self, user1_node: Node, user2_node: Node):
        friends_with_rel = Relationship(user1_node, "FRIENDS_WITH", user2_node)
        self.graph.create(friends_with_rel)

    def create_likes_relationship(self, user_node: Node, target_node: Node):
        likes_rel = Relationship(user_node, "LIKES", target_node)
        print(likes_rel)
        self.graph.create(likes_rel)