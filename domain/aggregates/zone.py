class Zone(object):

    def __init__(self,
                 formation,
                 well,
                 report,
                 type_completion,
                 type_boundaries):

        self._formation = formation
        self._well = well
        self._report = report
        self.type_completion = type_completion
        self.type_boundaries = type_boundaries

        self._formation.zones.append(self)
        self._well.zones.append(self)
