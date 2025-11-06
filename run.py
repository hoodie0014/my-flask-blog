from app import app
from app.data import db_session, api
from app.data.users import User
from flask_login import LoginManager


if __name__ == '__main__':
    db_session.global_init("app/db/blogs.db")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'unauthorized'


    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    app.register_blueprint(api.blueprint)

    app.run(debug=True)
