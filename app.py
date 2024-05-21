from flask import Flask, jsonify, abort
from typing import Tuple
import json

app = Flask(__name__)

def data_loader() -> Tuple[dict, dict]:
    """
    Функция загружает данные из json файлов и преобразует их в dict.
    Функция не должна нарушать изначальную структуру данных.
    """
    with open('data/posts.json', 'r') as f:
        posts = json.load(f)
    with open('data/comments.json', 'r') as f:
        comments = json.load(f)
    return posts, comments


@app.route("/")
def get_posts():
    """
    На странице / вывести json в котором каждый элемент - это:
    - пост из файла posts.json.
    - для каждой поста указано кол-во комментариев этого поста из файла comments.json

    Формат ответа:
    posts: [
        {
            id: <int>,
            title: <str>,
            body: <str>, 
            author: <str>,
            created_at: <str>,
            comments_count: <int>
        }
    ],
    total_results: <int>

    Порядок ключей словаря в ответе не важен
    """
    try:
        posts, comments = data_loader()
    except FileNotFoundError:
        abort(500, description="Data files not found.")
    except json.JSONDecodeError:
        abort(500, description="Error decoding JSON data.")

    output_posts = []
    for post in posts['posts']:
        comments_count = sum(1 for comment in comments['comments'] if comment['post_id'] == post['id'])
        output_posts.append({
            'id': post['id'],
            'title': post['title'],
            'body': post['body'],
            'author': post['author'],
            'created_at': post['created_at'],
            'comments_count': comments_count
        })

    return jsonify({
        'posts': output_posts,
        'total_results': len(output_posts)
    })


@app.route("/posts/<int:post_id>")
def get_post(post_id):
    """
    На странице /posts/<post_id> вывести json, который должен содержать:
    - пост с указанным в ссылке id
    - список всех комментариев к новости

    Отдавайте ошибку abort(404), если пост не существует.

    Формат ответа:
    id: <int>,
    title: <str>,
    body: <str>, 
    author: <str>,
    created_at: <str>
    comments: [
        "user": <str>,
        "post_id": <int>,
        "comment": <str>,
        "created_at": <str>
    ]

    Порядок ключей словаря в ответе не важен
    """
    try:
        posts, comments = data_loader()
    except FileNotFoundError:
        abort(500, description="Data files not found.")
    except json.JSONDecodeError:
        abort(500, description="Error decoding JSON data.")

    post = next((p for p in posts['posts'] if p['id'] == post_id), None)
    if not post:
        abort(404, description="Post not found.")
    
    post_comments = [comment for comment in comments['comments'] if comment['post_id'] == post_id]

    return jsonify({
        'id': post['id'],
        'title': post['title'],
        'body': post['body'],
        'author': post['author'],
        'created_at': post['created_at'],
        'comments': post_comments
    })


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify(error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True)
