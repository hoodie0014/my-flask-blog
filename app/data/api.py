from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from . import db_session
from .article import Article
from .comments import Comment

blueprint = Blueprint(
    'articles_api',
    __name__,
    template_folder='templates'
)


def sort_by_date(articles_list, value):
    if value == 'older':
        return articles_list.sort(key=lambda a: a.created_date, reverse=False)
    elif value == 'newer':
        return articles_list.sort(key=lambda a: a.created_date, reverse=True)


@blueprint.route('/api/articles')
def get_articles():
    category_param = request.args.get('category')
    sort_param = request.args.get('sort')

    db_sess = db_session.create_session()

    if category_param:
        articles = db_sess.query(Article).filter(Article.category == category_param).all()
    else:
        articles = db_sess.query(Article).all()

    if sort_param:
        sort_by_date(articles, sort_param)

    if not articles:
        return jsonify({'emptyList': True})

    return jsonify(
        {
            'ok': True,
            'articles':
                [item.to_dict(only=('id', 'title', 'category', 'created_date')) for item in articles]
        }
    )


@blueprint.route('/api/articles/<int:article_id>', methods=['GET'])
def get_one_article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)

    if not article:
        return jsonify({'notFound': True})

    article_data = {
        'id': article.id,
        'title': article.title,
        'category': article.category,
        'text': article.text,
        'created_date': article.created_date.isoformat() if article.created_date else None,
        'user': {
            'name': article.user.name,
            'id': article.user.id
        } if article.user else None
    }

    return jsonify({
        'ok': True,
        'article': article_data,
        'belongsToCurrentUser': current_user.is_authenticated and article.user.id == current_user.id
    })


@blueprint.route('/api/articles', methods=['POST'])
def create_article():
    if not request.json:
        return jsonify({'emptyRequest': True})
    elif not all(key in request.json for key in
                 ['title', 'text', 'category', 'user_id']):
        return jsonify({'notAllData': True})
    db_sess = db_session.create_session()
    article = Article()
    article.title = request.json['title']
    article.text = request.json['text']
    article.category = request.json['category']
    article.user_id = request.json['user_id']
    db_sess.add(article)
    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/articles/<int:article_id>', methods=['PUT'])
def edit_article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        return jsonify({'notFound': True})

    if not request.json:
        return jsonify({'emptyRequest': True})
    elif not all(key in request.json for key in
                 ['title', 'text', 'category', 'user_id']):
        return jsonify({'notAllData': True})

    article.title = request.json['title']
    article.text = request.json['text']
    article.category = request.json['category']
    article.user_id = request.json['user_id']

    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).get(article_id)
    if not article:
        return jsonify({'notFound': True})
    db_sess.delete(article)
    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/comment')
def get_comments():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).all()

    return jsonify(
        {
            'ok': True,
            'comments':
                [item.to_dict(only=('id', 'author_name', 'text', 'date', 'article_id')) for item in comments]
        }
    )


@blueprint.route('/api/comment/<int:comment_id>')
def get_one_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'notFound': True})

    return jsonify(
        {
            'ok': True,
            'comment': comment.to_dict(only=('id', 'author_name', 'text', 'date', 'article_id'))
        }
    )


@blueprint.route('/api/comment', methods=["POST"])
def create_comment():
    if not request.json:
        return jsonify({'emptyRequest': True})
    elif not all(key in request.json for key in
                 ['author_name', 'text', 'article_id']):
        return jsonify({'notAllData': True})
    db_sess = db_session.create_session()
    comment = Comment()
    comment.author_name = request.json['author_name']
    comment.text = request.json['text']
    comment.article_id = request.json['article_id']
    db_sess.add(comment)
    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/comment/<int:comment_id>', methods=["PUT"])
def edit_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)

    if not comment:
        return jsonify({'notFound': True})

    if not request.json:
        return jsonify({'emptyRequest': True})
    elif not all(key in request.json for key in
                 ['author_name', 'text', 'article_id']):
        return jsonify({'notAllData': True})

    comment.author_name = request.json['author_name']
    comment.text = request.json['text']
    comment.article_id = request.json['article_id']

    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/comment/<int:comment_id>', methods=["DELETE"])
def delete_comment(comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).get(comment_id)
    if not comment:
        return jsonify({'notFound': True})
    db_sess.delete(comment)
    db_sess.commit()
    return jsonify({'ok': True})


@blueprint.route('/api/article-comments/<int:article_id>')
def get_article_comments(article_id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.article_id == int(article_id)).all()

    if not comments:
        return jsonify({'emptyList': True})

    return jsonify(
        {
            'ok': True,
            'comments':
                [item.to_dict(only=('id', 'author_name', 'text', 'date', 'article_id')) for item in comments]
        }
    )


@blueprint.route('/api/logged-user')
@login_required
def check_logged_user():
    return jsonify({})


@blueprint.route('/api/current-user')
@login_required
def get_current_user():
    return jsonify({
        'name': current_user.name,
        'id': current_user.id
    })
