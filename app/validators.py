from wtforms import ( ValidationError)

# ------------------- Custom Validators ------------------- #

def length_check_username(form, field):
    if len(field.data) < 3:
        raise ValidationError("En az 3 karakter olmalı.")
    elif len(field.data) > 20:
        raise ValidationError("En fazla 20 karakter olmalı.")

def length_check_password(form, field):
    if len(field.data) < 5:
        raise ValidationError("En az 5 karakter olmalı.")
    elif len(field.data) > 20:
        raise ValidationError("En fazla 20 karakter olmalı.")