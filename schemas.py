from marshmallow import Schema, fields, ValidationError


class BytesField(fields.Field):
    def _validate(self, value):
        if not isinstance(value, bytes):
            raise ValidationError('Invalid input type.')

        if value is None or value == b'':
            raise ValidationError('Invalid value')


class DataSchema(Schema):
    date_added = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    status = fields.String()
    beautyTitle = fields.String()
    pereval_title = fields.String()
    other_titles = fields.String()
    connect = fields.Boolean()
    add_time = fields.DateTime(format='%Y-%m-%dT%H:%M:%S%z')
    fam = fields.String()
    name = fields.String()
    otc = fields.String()
    latitude = fields.Float()
    longitude = fields.Float()
    height = fields.Integer()
    winter = fields.String()
    summer = fields.String()
    spring = fields.String()
    autumn = fields.String()
    img_1_title = fields.String()
    img_1 = BytesField()
    img_2_title = fields.String()
    img_2 = BytesField()
    img_3_title = fields.String()
    img_3 = BytesField()

