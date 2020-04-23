from typing import List

from domain.aggregates.field import Field


class Project(object):

    def __init__(self,
                 name: str,
                 fields: List[Field]):

        self.name = name
        self.fields = fields
