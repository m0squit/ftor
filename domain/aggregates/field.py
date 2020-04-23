from typing import List

from domain.entities.formation import Formation
from domain.entities.well import Well


class Field(object):

    def __init__(self,
                 name: str,
                 formations: List[Formation],
                 wells: List[Well]):

        self.name = name
        self.formations = formations
        self.wells = wells
