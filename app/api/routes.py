from flask import Blueprint, request
from ..models import Post
from ..apiauthhelper import basic_auth_required, token_auth_required

api = Blueprint('api', __name__)

@api.route('/api/posts')
def getPosts():
    posts = Post.query.all()
    return {
        'status': 'ok',
        'totalResults': len(posts),
        'posts': [p.to_dict() for p in posts]
        #converts from post objects into an actual dictionary using the method we made in models
    }

@api.route('/api/posts/<int:post_id>')
def getPost(post_id):
    post = Post.query.get(post_id)
    if post:
        return {
            'status': 'ok',
            'totalResults': 1,
            'posts': 
            post.to_dict()
        }
    else:
        return {
            'status': 'not ok',
            'message': 'The post you are looking for does not exist.'
        }

@api.route('/api/posts/create')
def createPost(user):
    data = request.json()

    title = data['title']
    caption = data['caption']
    img_url = data['img_url']

    post = Post(title, img_url, caption, user.id)
    post.saveToDB

    return {
        'status': 'ok',
        'message': 'Successfully created post!'
    }