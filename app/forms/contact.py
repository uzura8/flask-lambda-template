import os
import re
from flask import current_app
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, Length


class Contact(FlaskForm):
    class Meta:
        csrf = False

    contact_type = RadioField('Kinds', choices=[], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(max=248)])
    name_phonetic = StringField('Phonetic Name',
                validators=[DataRequired(), Length(max=248)])
    email = StringField('Email',
                validators=[
                    DataRequired(),
                    Email(message='Email is invalid'),
                    Length(max=128)
                ])
    tel = StringField('Tel',
                validators=[DataRequired(), Length(min=10, max=11)])
    content = TextAreaField('Content', [DataRequired(), Length(max=3000)])
    recaptcha = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_app.config['CONTACT_RECAPTCHA_ENABLED']:
            self.recaptcha = RecaptchaField()


    @staticmethod
    def validate_tel(form, field):
        pattern = r'^(0[5-9]0[0-9]{8}|0[1-9][1-9][0-9]{7})$'
        matches = re.match(pattern, field.data)
        if matches is None:
            raise ValidationError('Tel is invalid')


    def get_dict(self):
        return {
            'contact_type': self.contact_type.data,
            'name': self.name.data,
            'name_phonetic': self.name_phonetic.data,
            'email': self.email.data,
            'tel': self.tel.data,
            'content': self.content.data,
        }
