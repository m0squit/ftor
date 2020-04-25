from typing import List

from domain.aggregates.field import Field
from domain.aggregates.zone import Zone


class Project(object):

    def __init__(self,
                 name: str,
                 zones: List[Zone],
                 fields: List[Field]):

        self.name = name
        self.zones = zones
        self.fields = fields
