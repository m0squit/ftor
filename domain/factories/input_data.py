from typing import Dict


class InputData(object):
    """Class for data in ObjectCreator to create project.

    Attributes:
        zone_dict:
        Dict as
        {well_name:
            {formation_name:
                {flood_data,
                 flux_data,
                 density,
                 viscosity,
                 volume_factor}}}
    """
    def __init__(self):
        self.formation_porosity_dict: Dict[str, float] = {}
        self.well_radius_dict: Dict[str, float] = {}
        self.zone_dict: Dict[str, dict] = {}
