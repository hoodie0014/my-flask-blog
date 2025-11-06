from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email


class FeedbackForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired('Это поле необходимо заполнить')])
    email = StringField('Email', validators=[DataRequired('Это поле необходимо заполнить'), Email('Некорректный адрес эл. почты')])
    message = TextAreaField('Сообщение', validators=[DataRequired('Это поле необходимо заполнить')])
    submit = SubmitField('Отправить')


class ArticleForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired('Это поле необходимо заполнить')])
    category = StringField('Категория', validators=[DataRequired('Выберите категорию')])
    article_text = TextAreaField('Текст статьи', validators=[DataRequired('Это поле необходимо заполнить')])


class CommentForm(FlaskForm):
    author_name = StringField('Имя автора', validators=[DataRequired('Это поле необходимо заполнить')])
    comment_text = TextAreaField('Текст комментария', validators=[DataRequired('Это поле необходимо заполнить')])


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Это поле необходимо заполнить')])
    password = PasswordField('Пароль', validators=[DataRequired('Это поле необходимо заполнить')])
    remember = BooleanField('Запомнить меня')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired('Это поле необходимо заполнить')])
    password = PasswordField('Пароль', validators=[DataRequired('Это поле необходимо заполнить')])
    name = StringField('Запомнить меня', validators=[DataRequired('Это поле необходимо заполнить')])
