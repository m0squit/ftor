from typing import List

from domain.aggregates.zone import Zone
from domain.entities.formation import Formation
from domain.entities.well import Well


class Project(object):

    def __init__(self,
                 field_name: str,
                 formations: List[Formation],
                 wells: List[Well],
                 zones: List[Zone]):

        self.field_name = field_name
        self.formations = formations
        self.wells = wells
        self.zones = zones
