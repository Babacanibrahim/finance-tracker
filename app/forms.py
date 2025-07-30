from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, DecimalField, DateField,
    BooleanField, validators)
from .validators import length_check_password , length_check_username

# ------------------- Formlar ------------------- #

# Şifremi unuttum
class ForgotPassword(FlaskForm):
    username = StringField("Kullanıcı adınız :", validators=[validators.DataRequired()])
    secret_quest = SelectField(
        "Gizli sorunuzu seçiniz :",
        choices=[
            ("pet", "Evcil hayvanınızın adı ?"),
            ("child", "Çocuğunuzun adı ?"),
            ("music", "En sevdiğiniz müzik türü ?"),
            ("secretkey", "Kendinize ait bir gizli anahtar ?")
        ]
    )
    answer = StringField("Gizli sorunun cevabı :")

# Şifre değiştirme
class ChangePassword(FlaskForm):
    password = PasswordField("* Parola :", validators=[
        validators.DataRequired(message="Lütfen bir parola giriniz."),
        length_check_password,
        validators.EqualTo("confirm", message="Lütfen parolalarınızı kontrol edin")
    ])
    confirm = PasswordField("* Parolanız tekrar :", validators=[validators.DataRequired()])

# Şifreyi yenileme
class RePassword(FlaskForm):
    current_password = PasswordField("Mevcut Parola :", validators=[
        validators.DataRequired("Güncel parolanız gerekli.")
    ])

# Giriş
class LoginForm(FlaskForm):
    username = StringField(" Kullanıcı adınız :", validators=[
        length_check_username,
        validators.DataRequired(message="Kullanıcı adı boş olamaz.")
    ])
    password = PasswordField(" Parola :", validators=[
        validators.DataRequired(message="Parola kısmı boş olamaz.")
    ])

# Kayıt
class RegisterForm(FlaskForm):
    name = StringField("İsim :")
    surname = StringField("Soyisim :")
    username = StringField("* Kullanıcı adınız :", validators=[
        length_check_username,
        validators.DataRequired(message="Kullanıcı adı boş olamaz.")
    ])
    email = StringField("E posta :", validators=[
        validators.optional(),
        validators.Email(message="Geçerli bir mail adresi giriniz.")
    ])
    secret_quest = SelectField(
        "Gizli sorunuzu seçiniz (şifrenizi unutmanız durumunda kullanılır opsiyoneldir)",
        choices=[
            ("", "Soru seçiniz."),
            ("pet", "Evcil hayvanınızın adı ?"),
            ("child", "Çocuğunuzun adı ?"),
            ("music", "En sevdiğiniz müzik tarzı ?"),
            ("secretkey", "Kendinize ait bir gizli anahtar ? (önerilmez)")
        ],
        validate_choice=False
    )
    answer = StringField("Gizli sorunun cevabı :")
    password = PasswordField("* Parola :", validators=[
        validators.DataRequired(message="Parola kısmı boş olamaz."),
        length_check_password,
        validators.EqualTo("confirm", message="Lütfen parolalarınızı kontrol edin")
    ])
    confirm = PasswordField("* Parolanız tekrar :", validators=[validators.DataRequired()])

# Profil Düzenleme
class ProfileEditForm(FlaskForm):
    name = StringField("İsim :")
    surname = StringField("Soyisim :")
    username = StringField("Kullanıcı adı :", validators=[
        length_check_username,
        validators.DataRequired(message="Kullanıcı adı boş olamaz.")
    ])
    email = StringField("E posta :", validators=[
        validators.optional(),
        validators.Email(message="Geçerli bir mail adresi giriniz.")
    ])
    secret_quest = SelectField(
        "Gizli sorunuzu seçiniz (şifrenizi unutmanız durumunda kullanılır opsiyoneldir)",
        choices=[],
        validate_choice=False
    )
    answer = StringField("Gizli sorunun cevabı :")
    password = PasswordField("Mevcut parolanızı girin :")
    allow_notifications = BooleanField('Bildirimleri almak istiyorum')

# Harcama ekleme
class ExpenseForm(FlaskForm):
    date = DateField("* Harcama Tarihi", format="%Y-%m-%d", validators=[
        validators.DataRequired(message="Tarih zorunlu alandır")
    ])
    amount = DecimalField("* Harcama Miktarı (TL olarak)", validators=[
        validators.DataRequired(message="Harcama miktarı zorunlu alandır.")
    ])
    category = SelectField("Harcama Kategorisi", coerce=int)

# Gelir ekleme
class IncomeForm(FlaskForm):
    date = DateField("* Gelir Tarihi", format="%Y-%m-%d", validators=[
        validators.DataRequired(message="Tarih zorunlu alandır")
    ])
    amount = DecimalField("* Gelir Miktarı (TL olarak)", validators=[
        validators.DataRequired(message="Gelir miktarı zorunlu alandır.")
    ])
    category = SelectField("Gelir Kategorisi", coerce=int)

# Limit ekleme adım 2
class BudgetStep2Form(FlaskForm):
    other_category_name = StringField("Diğer Kategori Adı", validators=[validators.Optional()])
    other_amount = DecimalField("Diğer Kategori Limiti", validators=[validators.Optional()])

# Limit ekleme adım 1
class BudgetStep1Form(FlaskForm):
    name = StringField("Harcamanız İçin Hatırlatıcı Bir İsim Belirleyin", validators=[validators.DataRequired()])
    start_date = DateField("Başlangıç Tarihi", format="%Y-%m-%d", validators=[validators.DataRequired()])
    end_date = DateField("Bitiş Tarihi", format="%Y-%m-%d", validators=[validators.DataRequired()])

# Formalite (kullanılmıyor)
class DeleteForm(FlaskForm):
    pass
