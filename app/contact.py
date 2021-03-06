import os
import json
import datetime
import configparser
import pytz
from flask import current_app, Blueprint, jsonify, request, render_template
from app.models.dynamodb import Contact, Service
from app.common.email import send_email_on_ses
from app.common.date import utc_iso
from app.common.error import InvalidUsage
from app.common.string import random_str
from app.forms.contact import Contact as ContactForm

bp = Blueprint('contact', __name__, url_prefix='/contacts')

PRJ_PREFIX = os.environ['PRJ_PREFIX']
ACCEPT_SERVICE_IDS = os.environ.get('ACCEPT_SERVICE_IDS', '').split(',')
SES_REGION = os.environ.get('SES_REGION')


@bp.route('/<string:service_id>', methods=['POST'])
def contats(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    config = set_service_ini(service_id)

    time_utc = utc_iso(True, True)
    timezone = validate_timezone(request.headers.get('Time-Zone', ''), config['default_timezone'])
    tz_local = pytz.timezone(timezone)
    time_local = datetime.datetime.now(tz_local).strftime('%Y/%m/%d %H:%M')

    form = ContactForm()
    form.contact_type.choices = config['type_choices']
    if config['gender_choices']:
        form.gender.choices = config['gender_choices']
    if not form.validate_on_submit():
        raise InvalidUsage('Requested data is invalid', 400, {'errors':form.errors})

    vals = form.get_dict()
    vals['serviceId'] = service_id
    vals['code'], vals['serviceIdCode'] = create_code(service_id)
    vals['createdAt'] = time_utc
    vals['updatedAt'] = time_utc
    vals['status'] = 0
    vals['subject'] = config['subject']
    vals['ip'] = request.remote_addr
    vals['ua'] = request.headers.get('User-Agent')
    Contact.create(vals)
    body = vals

    types = form.contact_type.choices
    body['contact_type_label'] = [ label for val, label in types if val == body['contact_type'] ][0]

    if body['gender']:
        genders = form.gender.choices
        body['gender_label'] = [ label for val, label in genders if val == body['gender'] ][0]
    body['created_at_formatted'] = time_local
    template_path = 'contact/{}/template.txt'.format(service_id)
    send_contact_email(body['email'], body['subject'], body, template_path,
                        config['email_from'], config['email_from_name'])
    return jsonify(body), 200


def set_service_ini(service_id):
    ini = configparser.ConfigParser()
    ini.read('config/contact/{}/config.ini'.format(service_id), encoding='utf-8')

    recaptcha_enabled = ini.get('recaptcha', 'enabled').lower() == 'true'
    current_app.config['CONTACT_RECAPTCHA_ENABLED'] = recaptcha_enabled
    if recaptcha_enabled:
        current_app.config['RECAPTCHA_USE_SSL'] = \
                ini.get('recaptcha', 'useSSL').lower() == 'true'
        current_app.config['RECAPTCHA_PUBLIC_KEY'] = ini.get('recaptcha', 'publicKey')
        current_app.config['RECAPTCHA_PRIVATE_KEY'] = ini.get('recaptcha', 'privateKey')

    res = {}
    res['subject'] = ini.get('mail', 'subject')
    res['email_from'] = ini.get('mail', 'emailFrom')
    res['email_from_name'] = ini.get('mail', 'emailFromName')
    res['default_timezone'] = ini.get('mail', 'defaultTimezone')

    types = json.loads(ini.get('form', 'types'))
    res['type_choices'] = [(i['val'], i['label']) for i in types]

    res['gender_choices'] = None
    items = {i[0]:i[1] for i in ini.items('form')}
    if 'genders' in items:
        genders = json.loads(ini.get('form', 'genders'))
        res['gender_choices'] = [(i['val'], i['label']) for i in genders]

    return res


def validate_timezone(req_tz, def_tz):
    if not req_tz:
        req_tz = def_tz

    if req_tz not in pytz.all_timezones:
        raise InvalidUsage('Timezone is invalid', 400)

    return req_tz


def create_code(service_id):
    code = None
    service_id_code = None
    useable_code = None
    loop_count = 0
    loop_max = 5
    while useable_code is None:
        code = random_str(6, True)
        service_id_code = '_'.join([service_id, code])
        item = Contact.get_one({'p': {'key':'serviceIdCode', 'val':service_id_code}})
        if not item:
            useable_code = code

        loop_count += 1
        if loop_count > loop_max:
            raise InvalidUsage('Create code error', 404)

    return code, service_id_code


def send_contact_email(email_to, subject, inputs, template_path, email_from, email_from_name=''):
    send_email_on_ses(
        subject,
        sender=(email_from_name, email_from),
        recipients=[email_to, email_from],
        text_body=render_template(
            template_path,
            email_to=email_to,
            inputs=inputs,
        ),
        region=SES_REGION
    )
