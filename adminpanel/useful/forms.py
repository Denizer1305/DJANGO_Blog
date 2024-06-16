from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import Length, Regexp, Email, DataRequired, EqualTo


class EditUsernameForm(FlaskForm):
    name = StringField("Логин", validators=[Length(min=4, max=25, message="Имя должно содержать от 4 до 25 символов"),
                                            Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                   message="Для имени пользователя разрешены только латинские буквы, "
                                                           "цифры и спецсимволы(без пробелов)."),
                                            ])
    submit = SubmitField("Сохранить изменения")


class EditEmailForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    submit = SubmitField("Сохранить изменения")


class EditPasswordForm(FlaskForm):
    old_psw = PasswordField("Старый пароль: ", validators=[DataRequired(), Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                                                  message="Для пароля разрешены "
                                                                                          "только  латинские буквы, "
                                                                                          "цифры и"
                                                                                          "спецсимволы(без пробелов)."),
                                                           Length(min=4, max=100,
                                                                  message="Пароль должен содержать от 4 до 100 "
                                                                          "символов")])
    new_psw = PasswordField("Новый пароль: ", validators=[DataRequired(), Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                                                 message="Для пароля разрешены "
                                                                                         "только  латинские буквы, "
                                                                                         "цифры и"
                                                                                         "спецсимволы(без пробелов)."),
                                                          Length(min=4, max=100,
                                                                 message="Пароль должен содержать от 4 до 100 "
                                                                         "символов")])
    psw2 = PasswordField("Повторите пароль: ",
                         validators=[DataRequired(), EqualTo('new_psw', message="Пароли должны совпадать")])
    submit = SubmitField("Сохранить изменения")


# def validate_category(field):
#     if field.data is None:
#         raise ValidationError("Необходимо выбрать категорию")


class AddPostForm(FlaskForm):
    title = StringField("Заголовок",
                        validators=[Length(min=2, max=300, message="Имя должно содержать от 2 до 300 символов"),
                                    DataRequired()],
                        description="Введите заголовок")
    category = SelectField("Категория")
    image = FileField('Картинка новости', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')],
                      description="Выберете файл")
    description = TextAreaField("Краткое описание новости",
                                validators=[
                                    Length(min=2, max=500, message="Имя должно содержать от 2 до 500 символов"),
                                    DataRequired()],
                                description="Краткое описание новости")
    text = TextAreaField("Текст новости", validators=[Length(min=10, max=10000, message="Поле 'текст' должно содержать "
                                                                                        "от 10 символов"),
                                                      DataRequired()],
                         description="Введите текст новости")
    submit = SubmitField("Добавить пост")


class EditPostForm(FlaskForm):
    edit_title = StringField("Заголовок",
                             validators=[Length(min=2, max=300, message="Имя должно содержать от 2 до 300 символов"),
                                         DataRequired()],
                             description="Введите заголовок")
    edit_category = SelectField("Категория")
    edit_image = FileField('Картинка новости', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')],
                           description="Выберете файл")
    edit_description = TextAreaField("Краткое описание новости",
                                     validators=[
                                         Length(min=2, max=500, message="Имя должно содержать от 2 до 500 символов"),
                                         DataRequired()],
                                     description="Краткое описание новости")
    edit_text = TextAreaField("Текст новости",
                              validators=[Length(min=10, max=10000, message="Поле 'текст' должно содержать "
                                                                            "от 10 символов"),
                                          DataRequired()],
                              description="Введите текст новости")
    submit = SubmitField("Сохранить изменения")


class DeletePostForm(FlaskForm):
    name = StringField("Вы уверены что хотите удалить пост?")
    submit = SubmitField("Да, удалить")


class EditCategoryForm(FlaskForm):
    name = StringField("Категория", validators=[Length(min=4, max=25, message="Название категории должно содержать от 4"
                                                                              "до 25 символов"), ],
                       description="Введите категорию")
    submit = SubmitField("Сохранить изменения")


class DeleteCategoryForm(FlaskForm):
    name = StringField("Вы уверены что хотите удалить категорию?",
                       validators=[Length(min=4, max=25, message="Название категории должно содержать от 4"
                                                                 "до 25 символов"), ],
                       description="Введите категорию")
    submit = SubmitField("Да, удалить")


class FilterForm(FlaskForm):
    period = SelectField("Период")
    category = SelectField("Категория")
    submit = SubmitField("Применить")
