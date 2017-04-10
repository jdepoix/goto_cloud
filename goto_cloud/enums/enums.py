from abc import ABCMeta, abstractstaticmethod


class Enum(metaclass=ABCMeta):
    """
    a class which is only used to store a set of static enum attributes
    """
    @classmethod
    def get_django_choices(cls):
        """
        :return: the enum attributes as a list of tuples, compatible with the django orm fields choices attribute
        :rtype: ((object, object,),)
        """
        attributes = cls.__dict__

        return tuple(
            (attribute, attributes[attribute],)
            for attribute in sorted(attributes.keys())
            if cls._is_enum_property(attributes, attribute)
        )

    @abstractstaticmethod
    def _is_enum_property(object_dict, attribute):
        """
        determines whether a given attribute is a enum property or not

        :param object_dict: the object the attribute belongs to
        :type object_dict: dict
        :param attribute: the name of the attribute
        :type attribute: str
        :return: is it an enum?
        :rtype: bool
        """
        pass


class StringEnum(Enum, metaclass=ABCMeta):
    """
    a enum class, with all static properties being strings
    """
    def _is_enum_property(object_dict, attribute):
        return (
            isinstance(object_dict[attribute], str)
            and not (attribute.startswith('__')
            and attribute.startswith('__'))
        )
