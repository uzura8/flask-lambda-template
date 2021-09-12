import re
from cerberus import Validator
from app.common.string import validate_url, validate_email


class ValidatorExtended(Validator):
    def _validate_valid_email(self, email, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (email and value and not validate_email(value)):
            self._error(field, 'email is invalid')


    def _validate_valid_tel(self, tel, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (tel and value and not re.match('^\d{10,11}$', value)):
            self._error(field, 'tel is invalid')


    def _validate_valid_url(self, url, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (url and value and not validate_url(value)):
            self._error(field, 'url is invalid')


class NormalizerExtended(Validator):
    pass


class NormalizerUtils():
    to_bool = lambda v: v.lower() in ('true', '1')
    to_bool_int = lambda v: 1 if v.lower() in ('true', '1') else 0
    trim = lambda v: v.strip() if type(v) is str else v
    rtrim = lambda v: v.rstrip() if type(v) is str else v
    split = lambda v, dlt=',': v.split(dlt)
