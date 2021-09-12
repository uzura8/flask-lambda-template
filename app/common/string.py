import re
import string
import random
import uuid
import ulid


def random_str(num, is_digits_only=False):
    if is_digits_only:
        population = string.digits
    else:
        population = string.ascii_letters + string.digits

    return ''.join(random.choices(population, k=num))


def new_uuid(fmt='ulid'):
    if fmt == 'ulid':
        return str(ulid.new()).lower()

    if fmt == 'uuidv4':
        return str(uuid.uuid4()).replace('-', '').lower()

    return str(uuid.uuid4()).replace('-', '').lower()


def validate_email(email):
    email = email.strip()
    if not email:
        return False

    pattern = '^([_a-z0-9-]+(\.[_a-z0-9-]+)*)' +\
             '@([a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4}))$'
    return re.findall(pattern, email)


def validate_url(url):
    return re.match('^https?://[\w\-\.\!~\*\'\(\);\/\?\:@&=+\$,%#]+$', url)
