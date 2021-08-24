import os
import re
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, Length

CONTACT_USE_RECAPTCHA = os.environ.get('CONTACT_USE_RECAPTCHA', 'False').lower() == 'true'


class Contact(FlaskForm):
    class Meta:
        csrf = False

    contact_type = RadioField('種別', choices=[], validators=[DataRequired()])
    name = StringField('名前', validators=[DataRequired(), Length(max=248)])
    name_phonetic = StringField('フリガナ',
                validators=[DataRequired(), Length(max=248)])
    email = StringField('メールアドレス',
                validators=[
                    DataRequired(),
                    Email(message='メールアドレスが正しくありません。'),
                    Length(max=128)
                ])
    tel = StringField('電話番号',
                validators=[DataRequired(), Length(min=10, max=11)])
    content = TextAreaField('内容', [DataRequired(), Length(max=3000)])
    recaptcha = None


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if CONTACT_USE_RECAPTCHA:
            self.recaptcha = RecaptchaField()


    @staticmethod
    def validate_tel(form, field):
        pattern = r'^(0[5-9]0[0-9]{8}|0[1-9][1-9][0-9]{7})$'
        matches = re.match(pattern, field.data)
        if matches is None:
            raise ValidationError('電話番号が正しくありません。')


    def get_dict(self):
        return {
            'contact_type': self.contact_type.data,
            'name': self.name.data,
            'name_phonetic': self.name_phonetic.data,
            'email': self.email.data,
            'tel': self.tel.data,
            'content': self.content.data,
        }
