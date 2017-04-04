from functools import reduce

from dict_utils.public import DictUtils


class BlueprintResolver():
    """
    takes care of resolving the dependencies of blueprints into one independent document
    """
    class ResolvingException(Exception):
        """
        is thrown, in case an error occurs, during resolving a blueprint
        """
        pass

    def __init__(self, base_blueprints):
        """
        is initialized with a set of base blueprints, which are used to resolve the given blueprints
        
        :param base_blueprints: set of base blueprints
        :type base_blueprints: dict
        """
        self.base_blueprints = base_blueprints

    def resolve(self, blueprint):
        """
        resolves the given blueprint with all its referencing dependency into one single blueprint
        
        :param blueprint: this either is a blueprint dict, or a sting id, referencing the parent directly
        :type blueprint: dict or str
        :return: resolved dict
        :rtype: dict
        :raises BlueprintResolver.ResolvingException: raised in case the blueprint is not valid and therefore can't be
        resolved
        """
        if isinstance(blueprint, str):
            return self._clean_representation(self._get_base_blueprint_by_id(blueprint))
        if isinstance(blueprint, dict):
            parents = self._get_parents(blueprint)
            return self._clean_representation(
                reduce(DictUtils.merge_dicts, [blueprint] + parents) if parents else blueprint
            )

        raise BlueprintResolver.ResolvingException(
            'following blueprint is not valid: {blueprint}'.format(blueprint=blueprint)
        )

    def _get_parents(self, blueprint):
        """
        returns all parents for a given blueprint
        
        :param blueprint: blueprint to get the parents for
        :type blueprint: dict
        :return: list of all parents. It is sorted with the nearest parent coming first
        :rtype: list
        """
        if 'parent' in blueprint:
            parent_blueprint = self._get_base_blueprint_by_id(blueprint['parent'])
            return [parent_blueprint] + self._get_parents(parent_blueprint)

        return []

    def _get_base_blueprint_by_id(self, id):
        """
        returns a base blueprint by id and validates the id
        
        :param id: the id of the blueprint to get
        :type id: str
        :return: the base blueprint
        :rtype: dict
        :raises BlueprintResolver.ResolvingException: raise if id is not found
        """
        if id not in self.base_blueprints:
            raise BlueprintResolver.ResolvingException(
                'blueprint is referencing a non existing base blueprint: {parent_blueprint_id}'.format(
                    parent_blueprint_id=id
                )
            )

        return self.base_blueprints[id]

    def _clean_representation(self, blueprint):
        """
        clean the blueprint of data, not relevant for the final representation
        
        :param blueprint: blueprint to clean
        :type: dict
        :return: cleaned blueprint
        :rtype: dict
        """
        blueprint.pop('parent', None)
        return blueprint
