from flask import Flask, request, abort
from flask.json import jsonify
from sql_classes import (get_latest_articles, posts_plus_comments, get_articles_by_author,
                         get_top_by_likes, get_posts, EditArticle, add_articles_database)

app = Flask(__name__)


@app.errorhandler(400)
def fucked_up(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(500)
def fucked_up_again(e):
    return jsonify(error=str(e)), 500


class ArticleValidationForm:
    def __init__(self, data):
        self.author = data.get('author')
        self.title = data.get('title')
        self.content = data.get('content')

        if not self.author or not self.title or\
           not self.content:
            raise Exception(f"{data}: Fields title, content, author should not be empty")
        if len(self.author) > 60 or\
           len(self.title) > 60:
            raise Exception("title and author fields should not be longer then 60 symbols")


def add_articles_v2(data):
    articles = []

    for unit in data:
        try:
            form = ArticleValidationForm(unit)
        except Exception as e:
            abort(400, description=str(e))

        articles.extend((form.title, form.content, form.author))

    try:
        ides = add_articles_database(articles)
    except Exception as e:
        print(f"failed while trying to add article: {e}")
        abort(400, description="something went wrong")
    return ides


@app.route('/add_articles', methods=['POST', 'GET'])
def post_article():
    try:
        validate_request_data(request)
    except Exception:
        raise

    try:
        list_ides = add_articles_v2(request.json)
    except Exception:
        raise
    return jsonify(list_ides)
    # return jsonify({'id': id})


def validate_request_data(req):
    if req.content_type != 'application/json':
        print('not json')
        return "not jason"
    data = req.json
    if not data:
        abort(500, "data is empty")
    if not isinstance(data, list):
        abort(500, 'Should be list')


"""-----------------------------------------------------------------------------------------------------------------"""

@app.route('/show_posts', methods=['GET', 'POST'])
def show_posts():
    if request.content_type != 'application/json':
        return "not jason"
    data = request.json
    if not data:
        return "no data"

    count = data.get('count')
    if data.get('by_likes'):
        posts = get_top_by_likes(count)
    elif data.get('by_date'):
        posts = get_latest_articles(count)
    elif author := data.get('author'):
        posts = get_articles_by_author(author)
    else:
        ids = data.get('ids')
        if not ids:
            abort(400, description="no parameters were chosen")
        posts = get_posts(ids)
    result = posts_plus_comments(posts)
    return jsonify(result)


@app.route('/update_post', methods=['put'])
def update_post():
    data = request.json
    if not data:
        abort(500, "no data")
    post_id = data.get("post_id")
    if not post_id:
        abort(500, "post_id is required")

    edited_post = EditArticle(post_id)
    try:
        edited_post.check_if_exists()
    except Exception as e:
        abort(400, e)

    if new_title := data.get("title"):
        if len(new_title) > 60:
            abort(500, "title and author fields should not be longer then 60 symbols")
        edited_post.edit_title(new_title)
    if new_content := data.get("content"):
        edited_post.edit_content(new_content)
    if likes := data.get('likes'):
        if isinstance(likes, int) and likes > 0:
            edited_post.add_like()
        else:
            abort(500, "likes field should be positive integer")


if __name__ == '__main__':
    app.run(debug=True)
