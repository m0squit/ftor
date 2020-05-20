from domain.aggregates.project import Project


class Calculator(object):
    """Domain objects calculation manager."""

    @classmethod
    def run(cls, project: Project) -> Project:
        project = cls._calc_wells(project)
        project.calc_metric()
        return project

    @staticmethod
    def _calc_wells(project: Project) -> Project:
        for well in project.wells:
            print(well.name)
            well.calc()
        return project
