import apiflask
from apiflask import fields
from apiflask import validators
from marshmallow_dataclass import class_schema

from ....schemas import public


class ListPagination(apiflask.Schema):
    limit = fields.Integer()


ProcessList = class_schema(public.ProcessList)
