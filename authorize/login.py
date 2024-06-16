from flask import Blueprint, render_template, flash, redirect, url_for, make_response, request
from flask_login import current_user, login_required, login_user, logout_user
from authorize.useful.forms import LoginForm, RegisterForm
from models import User
from connect_db import db

user = Blueprint('authorize', __name__, template_folder='templates', static_folder='static')


# @user.route("/")
# @login_required
# def index():
#     return render_template("authorize/del-profile.html", title='Авторизация')


@user.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.name.data).first() is not None:
            print(f"Пользователь с именем {form.name.data} уже есть в БД")
            flash(f"Пользователь с именем {form.name.data} уже есть в БД", category="error")
        elif User.query.filter_by(email=form.email.data).first() is not None:
            print(f"Пользователь с email'ом {form.email.data} уже есть в БД")
            flash(f"Пользователь с email'ом {form.email.data} уже есть в БД", category="error")
        else:
            try:
                add_user = User(username=form.name.data, email=form.email.data)
                add_user.set_password(form.psw.data)
                db.session.add(add_user)
                db.session.commit()
                return redirect(url_for('authorize.login'))
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")

    return render_template("authorize/register.html", title="Регистрация", form=form)


@user.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('adminPanel.profile'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            find_user = User.query.filter_by(username=form.name.data).first()
            if find_user and find_user.check_password(form.psw.data):
                login_user(find_user, remember=form.remember.data)
                print("User is found")
                return redirect(request.cookies.get("next") or url_for('adminPanel.profile'))
            else:
                flash("Неверная пара логин/пароль", category="error")
        except:
            print("Ошибка чтения бд")
            flash("Ошибка чтения бд", category="error")

    return render_template("authorize/login.html", title="Авторизация", form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie('next')
    flash("Вы вышли из аккаунта", "success")
    return resp
