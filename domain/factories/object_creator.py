from domain.entities.formation import Formation


class ObjectCreator(object):

    @staticmethod
    def create_formation(name, reservoir, fluid):

        formation = Formation()
        return formation
