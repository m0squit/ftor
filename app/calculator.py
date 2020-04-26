from domain.aggregates.project import Project


class Calculator(object):

    @staticmethod
    def run(project: Project) -> Project:
        for zone in project.zones:
            zone.predict()
        return project
