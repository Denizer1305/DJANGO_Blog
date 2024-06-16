import datetime
import locale

import flask
from flask import Flask, render_template, make_response, request, send_from_directory, flash
from sqlalchemy import or_

# from flask_login import current_user

from connect_db import db, login
from models import User, Category, Post
from authorize.login import user
from adminpanel.admin import admin
from useful.forms import FilterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_site.db'
app.config["SECRET_KEY"] = "wewrtrtey1223345dfgdf"
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
login.init_app(app)

login.login_view = 'no_authorized'
login.login_message = 'Авторизируетесь для доступа к закрытым страницам'
login.login_message_category = 'success'

locale.setlocale(locale.LC_ALL, 'ru_RU')

app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(admin, url_prefix="/admin")


@login.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


# @app.before_request
# def before_request():
#     db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    form = FilterForm()

    form.category.choices = [("", "Все категории")]
    form.category.choices += ([(option.id, option.name) for option in Category.query.all()])

    form.period.choices = [("", "Всё время"),
                           ("1", "Сегодня"),
                           ("2", "Последняя неделя"),
                           ("3", "Последний месяц")]

    posts = Post.query.join(Category).join(User).add_columns(Post.id,
                                                             Post.title,
                                                             Post.desc,
                                                             Post.filename,
                                                             Post.date,
                                                             Category.name,
                                                             User.username
                                                             )

    if request.method == "POST":
        if form.validate_on_submit():
            if form.period.data == "1":
                period = datetime.datetime.now() - datetime.timedelta(days=1)
            elif form.period.data == "2":
                period = datetime.datetime.now() - datetime.timedelta(weeks=1)
            elif form.period.data == "3":
                period = datetime.datetime.now() - datetime.timedelta(days=30)
            else:
                period = ""
            posts = (Post.query.
                     join(Category).join(User).add_columns(Post.id,
                                                           Post.title,
                                                           Post.desc,
                                                           Post.filename,
                                                           Post.date,
                                                           Category.name,
                                                           User.username
                                                           )).filter(
                or_(form.category.data == "", Post.category_id == form.category.data),
                or_(form.period.data == "", Post.date >= period))

        else:
            flash(f"Ошибка валидации", category="error")

    return render_template("index.html", form=form, posts=posts, title="Главная")


@app.route("/show_post/<alias>")
def show_post(alias):
    post = Post.query.filter_by(id=alias).join(Category).join(User).add_columns(Post.id,
                                                                                Post.title,
                                                                                Post.post,
                                                                                Post.date,
                                                                                Category.name,
                                                                                User.username
                                                                                ).first()

    return render_template('show_post.html', post=post, title="Пост")


@app.route('/no_authorized')
def no_authorized():
    resp = make_response(render_template("no_authorized.html", title="Авторизуйтесь"))
    if request.args.get('next'):
        resp.set_cookie('next', request.args.get('next'))
    return resp


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(flask.current_app.config['UPLOAD_FOLDER'], filename)


@app.template_filter('formatdatetime')
def format_datetime(value, format='%B %d, %Y %H:%M'):
    if value is None:
        return ""
    return value.strftime(format)


if __name__ == "__main__":
    app.run(debug=True)
