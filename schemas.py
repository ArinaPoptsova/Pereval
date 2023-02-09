import datetime
import re

from marshmallow import Schema, fields, ValidationError, validate


class BytesField(fields.Field):
    def _validate(self, value):
        if not isinstance(value, bytes):
            raise ValidationError('Invalid input type.')

        if value is None or value == b'':
            raise ValidationError('Invalid value')


def validate_email(email):
    if not re.match(r'([a-zA-Z0-9_.+-]+)@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9_.+-]', email):
        raise ValidationError('Невалидный адрес электронной почты')

def validate_phone(phone):
    if not re.match(r'[0-9+ ().x-]+\Z', phone):
        raise ValidationError('Невалидный номер телефона')


class UserSchema(Schema):
    fam = fields.String(required=True)
    name = fields.String(required=True)
    otc = fields.String(required=True)
    email = fields.Email(required=True, validate=validate_email)
    phone = fields.String(required=True, validate=validate_phone)


class CoordsSchema(Schema):
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    height = fields.Integer(required=True)

class LevelSchema(Schema):
    winter = fields.String()
    summer = fields.String()
    spring = fields.String()
    autumn = fields.String()


class ImageSchema(Schema):
    title = fields.String()
    data = BytesField(attribute='img')


class DataSchema(Schema):
    date_added = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z', required=True,
                                 validate=validate.Range(max=datetime.datetime.utcnow()))
    status = fields.String(required=True, validate=validate.OneOf(['new', 'pending', 'accepted', 'rejected']))
    beautyTitle = fields.String()
    pereval_title = fields.String(required=True, validate=validate.Length([1, 255]))
    other_titles = fields.String()
    connect = fields.String()
    add_time = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z', required=True,
                               validate=validate.Range(max=datetime.datetime.utcnow()))
