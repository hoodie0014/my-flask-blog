from flask import render_template, request, redirect, url_for, jsonify, make_response
from flask_login import login_user, login_required, logout_user, current_user

from app import app
from app.forms import FeedbackForm, ArticleForm, CommentForm, LoginForm, RegisterForm
from datetime import datetime
from app.data import db_session
from app.data.article import Article
from app.data.comments import Comment
from app.data.users import User


@app.route('/')
def index():
    db_sess = db_session.create_session()
    articles_list = db_sess.query(Article).all()
    articles_list.sort(key=lambda a: a.created_date, reverse=True)

    if len(articles_list) >= 4:
        articles_list = articles_list[:4]

    today = datetime.now().date()

    return render_template('index.html', articles=articles_list, today=today)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    feedback_response = {}
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        feedback_response = {
            'is_response': True,
            'user_name': name,
            'user_email': email,
        }
    return render_template('feedback.html', form=form, feedback_response=feedback_response)


def sort_by_date(articles_list, value):
    if value == 'older':
        return articles_list.sort(key=lambda a: a.created_date, reverse=False)
    elif value == 'newer':
        return articles_list.sort(key=lambda a: a.created_date, reverse=True)


@app.route('/articles')
def articles():
    category_param = request.args.get('category')
    sort_param = request.args.get('sort')

    db_sess = db_session.create_session()

    if category_param:
        articles = db_sess.query(Article).filter(Article.category == category_param).all()
    else:
        articles = db_sess.query(Article).all()

    if sort_param:
        sort_by_date(articles, sort_param)
    else:
        sort_by_date(articles, 'newer')

    today = datetime.now().date()

    return render_template('articles.html', articles=articles, today=today, sort_param=sort_param, category_param=category_param)


@app.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).filter(Article.id == int(id))

    form = CommentForm()
    if request.method == "POST" and form.validate_on_submit() :
        comment = Comment()
        comment.article_id = id
        comment.text = form.comment_text.data
        comment.author_name = form.author_name.data
        db_sess.add(comment)
        db_sess.commit()

        return redirect(url_for('article', id=id))

    if article:
        return render_template('article.html', article=article, form=form)
    return "Статья не найдена", 404


@app.route('/create-article', methods=['GET', 'POST'])
@login_required
def create_article():
    form = ArticleForm()

    if form.validate_on_submit():
        article = Article()
        article.title = form.title.data
        article.text = form.article_text.data
        article.category = form.category.data
        article.user_id = current_user.id

        db_sess = db_session.create_session()
        db_sess.add(article)
        db_sess.commit()

        return redirect(url_for('create_article_success'))

    return render_template('article-form.html', form=form, action='Создать')


@app.route('/create-article/success')
@login_required
def create_article_success():
    return render_template('article-success.html', action='создана')


@app.route('/delete-article/<int:id>')
@login_required
def delete_article(id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).filter(Article.id == id).first()

    if article.user == current_user:
        db_sess.delete(article)
        db_sess.query(Comment).filter(Comment.article_id == id).delete()
        db_sess.commit()

        return redirect(url_for('delete_article_success'))

    return redirect(url_for('not_allowed'))


@app.route('/delete-article/success')
@login_required
def delete_article_success():
    return render_template('article-success.html', action='удалена')


@app.route('/edit-article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    db_sess = db_session.create_session()
    article = db_sess.query(Article).filter(Article.id == id).first()

    if article.user == current_user:
        form_inserted = ArticleForm()
        form_inserted.title.data = article.title
        form_inserted.article_text.data = article.text
        form_inserted.category.data = article.category

        form = ArticleForm()

        if form.validate_on_submit():
            article.title = form.title.data
            article.text = form.article_text.data
            article.category = form.category.data
            db_sess.commit()

            return redirect(url_for('edit_article_success', id=id))

        return render_template('article-form.html', form=form_inserted, action='Редактировать')

    return redirect(url_for('not_allowed'))


@app.route('/edit-article/<int:id>/success')
@login_required
def edit_article_success(id):
    return render_template('article-success.html', action='отредактирована')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=login_form)

    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == register_form.email.data).first():
            return render_template('register.html',
                                   form=register_form,
                                   message="Такой пользователь уже есть")

        user = User()
        user.name = register_form.name.data
        user.email = register_form.email.data
        user.set_password(register_form.password.data)
        db_sess.add(user)
        db_sess.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=register_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/unauthorized')
def unauthorized():
    return render_template('not-allowed.html',
                           message='Вы не можете создавать/редактировать/удалять статьи без входа в аккаунт!')


@app.route('/not-allowed')
def not_allowed():
    return render_template('not-allowed.html',
                           message='Вы не можете редактировать/удалять чужие статьи!')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
