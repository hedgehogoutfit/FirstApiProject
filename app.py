from flask import Flask, request, abort
from flask.json import jsonify
from sql_classes import (get_latest_posts, get_posts_by_author,
                         get_top_by_likes, get_posts, EditArticle, add_post)

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
            abort(code=400, description=f"{data}: Fields title, content, author should not be empty")
        if len(self.author) > 60 or\
           len(self.title) > 60:
            abort(code=400, description="title and author fields should not be longer then 60 symbols")




@app.route('/add_post', methods=['POST', 'GET'])
def post_article():
    validate_request_data(request)
    form = ArticleValidationForm(request.json)
    try:
        post_id = add_post(title=form.title, author=form.author, content=form.content)
    except Exception:
        abort(400, description="something went wrong")
    return post_id


def validate_request_data(req):
    if req.content_type != 'application/json':
        abort(500, "content type must be application/json")
    if not req.json:
        abort(500, "data is empty")


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
def show_post(id):
    return get_posts([id])

@app.route('/posts', methods=['GET', 'POST'])
def show_posts():
    """/posts?param=by_date"""
    param = request.args.get('param')
    count = request.args.get('count', 5)
    if param == 'by_likes':
        posts = get_top_by_likes(count)
    elif param == 'by_date':
        posts = get_latest_posts(count)
    return posts


@app.route('/update_post', methods=['put'])
def update_post():
    """example json: {"post_id": "2", "content": "new content"}"""
    validate_request_data(request)
    data = request.json
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
    return {"info": f"the post with id {post_id} was updated"}

if __name__ == '__main__':
    app.run(debug=True)
