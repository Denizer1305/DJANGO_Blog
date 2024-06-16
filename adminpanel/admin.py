import datetime
import os

import flask
from flask import (Blueprint, render_template, request, redirect, url_for, flash, make_response,
                   send_from_directory, session)
from flask_login import login_required, current_user, logout_user
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from adminpanel.useful.forms import (EditUsernameForm,
                                     EditEmailForm,
                                     EditPasswordForm,
                                     EditCategoryForm,
                                     DeleteCategoryForm,
                                     AddPostForm, EditPostForm, DeletePostForm, FilterForm)
from connect_db import db
from models import User, Category, Post

admin = Blueprint('adminPanel', __name__, template_folder='templates', static_folder='static')

menu = [
    {"name": "Добавить пост", "url": "adminPanel.posts"},
    {"name": "Категории", "url": "adminPanel.category"},
    {"name": "Посты", "url": "adminPanel.posts"},
    {"name": "Профиль", "url": "adminPanel.profile"},
]


@admin.route("/")
@admin.route("/profile")
@login_required
def profile():
    forms = {'post': {'add': AddPostForm(),
                      'edit': {'username': EditUsernameForm(),
                               'email': EditEmailForm(),
                               'password': EditPasswordForm()}}}
    add_category_choices(forms['post']['add'])

    l_form = {}

    return render_template("adminPanel/profile.html", menu=menu, forms=forms,
                           l_form=l_form, title='Авторизация')


@admin.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_username():
    if request.method == "POST":
        form = EditUsernameForm(request.form)
        if form.validate_on_submit() and User.query.filter_by(username=form.name.data).first() is None:
            user = User.query.get(current_user.id)
            lost_name = user.username
            user.username = form.name.data
            db.session.add(user)
            db.session.commit()
            flash(f"Логин {lost_name} успешно изменен на {user.username}", category="success")
        else:
            flash(f"Измените логин {form.name.data}. Такой никнейм уже занят", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/edit_email", methods=["GET", "POST"])
@login_required
def edit_email():
    if request.method == "POST":
        form = EditEmailForm(request.form)
        if form.validate_on_submit() and User.query.filter_by(email=form.email.data).first() is None:
            user = User.query.get(current_user.id)
            lost_email = user.email
            print(f"lost-mail {lost_email}")
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash(f"E-mail {lost_email} успешно изменен на {user.email}", category="success")
        else:
            flash(f"Измените e-mail {form.email.data}. Такой e-mail уже занят", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/edit_password", methods=["GET", "POST"])
@login_required
def edit_password():
    if request.method == "POST":
        form = EditPasswordForm(request.form)
        user = User.query.get(current_user.id)
        print(f"password - {user.check_password(form.old_psw.data)}")
        if form.validate_on_submit() and user.check_password(form.old_psw.data):
            try:
                user.set_password(form.new_psw.data)
                db.session.add(user)
                db.session.commit()
                flash(f"Пароль успешно изменен.", category="success")
            except:
                db.session.rollback()
                print("Ошибка записи в БД при изменении пароля. adminPanel.edit_password")
                flash(" записи в БД при изменении пароля.", category="error")
        else:
            flash(f"Неверный пароль. Попробуйте еще раз", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/delete_profile", methods=["GET", "POST"])
@login_required
def delete_profile():
    if request.method == "POST":
        try:
            user = User.query.get(current_user.id)
            if user.check_password(request.form["psw"]):
                db.session.delete(user)
                db.session.commit()
                logout_user()
                resp = make_response(redirect(url_for("no_authorized")))
                resp.delete_cookie('next')
                print("Пользователь удален")
                flash(f"Пользователь {user.username} успешно удален", category="success")
                return resp
            else:
                flash(f"Неверный пароль. Попробуйте еще раз", category="error")
        except:
            db.session.rollback()
            print("Ошибка удаления из бд. adminPanel.delete_profile")
            flash("Ошибка удаления из бд", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/category")
@login_required
def category():
    forms = {'post': {'add': AddPostForm()},
             'category': {'add': EditCategoryForm(),
                          'edit': EditCategoryForm(),
                          'delete': DeleteCategoryForm()}}
    add_category_choices(forms['post']['add'])

    l_form = {}
    categories = Category.query.all()

    open_modal_add_cat = request.cookies.get('open_modal_add_cat')
    resp = make_response(render_template("adminPanel/category.html", menu=menu, forms=forms,
                                         l_form=l_form, categories=categories,
                                         open_modal_add_cat=open_modal_add_cat, title='Категории'))
    resp.delete_cookie('open_modal_add_cat')
    return resp


@admin.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        form_a = EditCategoryForm()
        if form_a.validate_on_submit() and Category.query.filter_by(name=form_a.name.data).first() is None:
            try:
                add_cat = Category(name=form_a.name.data)
                db.session.add(add_cat)
                db.session.commit()
                flash("Категория успешно добавлена", "success")
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")
        else:
            print(f"Категория '{form_a.name.data}' уже есть в БД")
            flash(f"Категория '{form_a.name.data}' уже есть в БД", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route("/edit_category/<alias>", methods=["GET", "POST"])
@login_required
def edit_category(alias):
    print(alias)
    form_e = EditCategoryForm()
    if request.method == "POST":
        if form_e.validate_on_submit() and Category.query.filter_by(name=form_e.name.data).first() is None:
            try:
                edit_cat = Category.query.filter_by(id=alias).first()
                edit_cat.name = form_e.name.data
                print(f"edit_cat- {edit_cat.name}")
                db.session.add(edit_cat)
                db.session.commit()
                flash("Категория успешно изменена", "success")
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")
        else:
            print(f"Категория '{form_e.name.data}' уже есть в БД")
            flash(f"Категория '{form_e.name.data}' уже есть в БД", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route("/delete_category/<alias>", methods=["GET", "POST"])
@login_required
def delete_category(alias):
    form_d = DeleteCategoryForm()
    delete_cat = Category.query.filter_by(id=alias).first()
    if request.method == "POST":
        if (form_d.validate_on_submit() and form_d.name.data == "delete"
                and Post.query.filter_by(category_id=alias).first() is None):
            try:
                db.session.delete(delete_cat)
                db.session.commit()
                flash("Категория успешно удалена", "success")
            except:
                db.session.rollback()
                print("Ошибка удаления категории из бд")
                flash("Ошибка удаления категории из бд", category="error")
        else:
            print(f"Категория '{delete_cat.name}' не удалена из БД. Есть связанные посты")
            flash(f"Категория '{delete_cat.name}' не удалена из БД. Есть связанные посты", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route('/uploads/<filename>')
@login_required
def send_file(filename):
    return send_from_directory(flask.current_app.config['UPLOAD_FOLDER'], filename)


@admin.route("/posts", methods=["GET", "POST"])
@login_required
def posts():
    forms = {'post': {'add': AddPostForm(),
                      'delete': DeletePostForm()},
             'filter': FilterForm()}
    add_category_choices(forms['post']['add'])
    forms['filter'].category.choices = [("", "Все категории")]
    forms['filter'].category.choices += ([(option.id, option.name) for option in Category.query.all()])

    forms['filter'].period.choices = [("", "Всё время"),
                                      ("1", "Сегодня"),
                                      ("2", "Последняя неделя"),
                                      ("3", "Последний месяц")]

    l_form = {}

    posts = Post.query.filter_by(user_id=current_user.id).join(Category).add_columns(Post.id,
                                                                                     Post.title,
                                                                                     Post.desc,
                                                                                     Post.date,
                                                                                     Post.filename,
                                                                                     Category.name)
    if session.get('form_data'):
        l_form = session.pop('form_data')

    if request.method == "POST":
        if forms['filter'].validate_on_submit():
            if forms['filter'].period.data == "1":
                period = datetime.datetime.now() - datetime.timedelta(days=1)
            elif forms['filter'].period.data == "2":
                period = datetime.datetime.now() - datetime.timedelta(weeks=1)
            elif forms['filter'].period.data == "3":
                period = datetime.datetime.now() - datetime.timedelta(days=30)
            else:
                period = ""
            posts = (Post.query.
                     join(Category).join(User).add_columns(Post.id,
                                                           Post.title,
                                                           Post.desc,
                                                           Post.filename,
                                                           Post.date,
                                                           Post.user_id,
                                                           Category.name,
                                                           User.username
                                                           )).filter(
                or_(Post.user_id == current_user.id),
                or_(forms['filter'].category.data == "", Post.category_id == forms['filter'].category.data),
                or_(forms['filter'].period.data == "", Post.date >= period))

        else:
            flash(f"Ошибка валидации", category="error")

    [print(post) for post in posts]

    return render_template("adminPanel/post.html", menu=menu, forms=forms, posts=posts,
                           l_form=l_form, title='Мои посты')


@admin.route("/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    form = AddPostForm()
    add_category_choices(form)
    if request.method == "POST":
        if form.validate_on_submit() and form.category.data:
            try:
                add_post_to_db = Post(title=form.title.data,
                                      category_id=form.category.data,
                                      desc=form.description.data,
                                      post=form.text.data,
                                      user_id=current_user.id
                                      )

                if form.image.data:
                    add_post_to_db.filename = upload_image(form.image.data, add_post_to_db.id)

                flash("Пост успешно добавлен", "success")
                db.session.add(add_post_to_db)
                db.session.commit()
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")
        else:
            if len(form.category.choices) == 1:
                resp = redirect(url_for('adminPanel.category'))
                resp.set_cookie('open_modal_add_cat', 'True')
                flash("Создайте категорию для добавления поста.", category="error")
                return resp

            if not form.category.data:
                session['form_data'] = request.form.to_dict()
                flash("Вы не выбрали категорию. Пост не сохранен в БД.", category="error")
                return redirect(url_for('adminPanel.posts'))

            session['form_data'] = request.form.to_dict()
            flash("Проверьте поля", category="error")

    return redirect(url_for('adminPanel.posts'))


@admin.route("/edit_post/<alias>", methods=["GET", "POST"])
@login_required
def edit_post(alias):
    l_form = {}
    forms = {'post': {'add': AddPostForm(),
                      'edit': EditPostForm()}}

    forms["post"]["edit"].edit_category.choices = [("", "Выберите категорию")]
    forms["post"]["edit"].edit_category.choices += ([(option.id, option.name) for option in Category.query.all()])

    current_post = (Post.query.filter_by(id=alias).join(Category).
                    add_columns(Post.id, Post.title, Post.desc, Post.filename,
                                Post.post, Post.category_id, Category.name).first())

    if request.method == "POST":
        if forms["post"]["edit"].validate_on_submit() and forms["post"]["edit"].edit_category.data:
            try:
                edit_post_to_db = Post.query.filter_by(id=alias).first()
                edit_post_to_db.title = forms["post"]["edit"].edit_title.data
                edit_post_to_db.desc = forms["post"]["edit"].edit_description.data
                edit_post_to_db.post = forms["post"]["edit"].edit_text.data
                edit_post_to_db.user_id = current_user.id
                edit_post_to_db.category_id = forms["post"]["edit"].edit_category.data

                if forms["post"]["edit"].edit_image.data:
                    edit_post_to_db.filename = upload_image(forms["post"]["edit"].edit_image.data, edit_post_to_db.id)

                db.session.add(edit_post_to_db)
                db.session.commit()
                flash("Пост успешно изменен", "success")
                return redirect(url_for('adminPanel.posts'))

            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")

        else:
            if not forms["post"]["edit"].edit_category.data:
                flash("Вы не выбрали категорию. Пост не сохранен в БД.", category="error")
                return redirect(url_for(f'adminPanel.edit_post', alias=current_post.id))

            flash("Проверьте поля", category="error")

    return render_template('adminPanel/edit_post.html', menu=menu, forms=forms, l_form=l_form,
                           current_post=current_post, title='Редактирование поста')


@admin.route("/delete_post/<alias>", methods=["GET", "POST"])
@login_required
def delete_post(alias):
    form = DeletePostForm()
    deleted_post = Post.query.filter_by(id=alias).first()
    if request.method == "POST":
        if form.validate_on_submit() and form.name.data == "delete":
            try:
                db.session.delete(deleted_post)
                db.session.commit()
                flash("Пост успешно удален", "success")
            except:
                db.session.rollback()
                print("Ошибка удаления категории из бд")
                flash("Ошибка удаления поста из бд", category="error")
        else:
            print(f"Пост не удален из БД.")
            flash(f"Пост не удален из БД.", category="error")
    return redirect(url_for('adminPanel.posts'))


def add_category_choices(form):
    form.category.choices = [("", "Выберите категорию")]
    form.category.choices += ([(option.id, option.name) for option in Category.query.all()])


def upload_image(image, post_id):
    # Создаю имя файла вида: "image_p"+"post.id" + ".расширение исходного файла"
    last_part = image.filename.split('.')[-1]
    filename = secure_filename(f"image_p{post_id}.{last_part}")

    # Создаю директорию "uploads", если ее нет
    os.makedirs(flask.current_app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Сохраняю файл с новым именем в директории "uploads"
    image.save(os.path.join(flask.current_app.config['UPLOAD_FOLDER'], filename))
    return filename
