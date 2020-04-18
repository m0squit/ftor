from domain.zone import Zone


class Field(object):
    """Class for field description.

    """
    def __init__(self,
                 name,
                 wells,
                 formations,
                 library_data):
        """Inits field and creates well-formation zone object.

        Args:
            wells (list): A list of well type objects.
            formations (list): A list of formation type objects.
            library_data (dict): A dict from well-formations names as keys and zone data as values.
                For example: library_data = {'name_well': {'name_formation': data}}
        """
        self.name = name
        self.wells = wells
        self.formations = formations
        self._library_data = library_data
        self._create_zones()

    def _create_zones(self):
        self.zones = []
        for well in self.wells:
            library_data_well = self._library_data[well.name]
            for name_formation, data in library_data_well.items():
                formation = self._get_formation(name_formation)
                zone = Zone(well, formation, data)
                well.zones.append(zone)
                formation.zones.append(zone)
                self.zones.append(zone)

    def _get_formation(self, name_formation):
        for formation in self.formations:
            if formation.name == name_formation:
                return formation
