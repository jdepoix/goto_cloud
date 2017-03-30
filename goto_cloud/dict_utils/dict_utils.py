import operator
from functools import reduce


class DictUtils():
    """
    collection of static methods, helping with dicts
    """
    @staticmethod
    def flatten_child_elements(dic):
        """
        flattens all child keys, and values of a tree-like dict
        
        :param dic: the dict to get the children for
        :type dic: dict
        :return: flat child values
        :rtype: list
        """
        if isinstance(dic, dict):
            return (
                reduce(
                    operator.add,
                    [(DictUtils.flatten_child_elements(child)) for child in dic.values()] + [list(dic.keys())]
                )
                if dic else []
            )
        else:
            return [dic]


    @staticmethod
    def find_sub_dict_by_key(dic, key):
        """
        traverses over a tree like dict structure in order, and returns the first "sub-dict" which keys matches the
        given key
        
        :param dic: the dict to search in
        :type dic: dict
        :param key: the key to look for
        :type key: str
        :return: the sub dict, or None if none was found
        :rtype: dict
        """
        if isinstance(dic, dict):
            if key in dic.keys():
                return dic[key]
            else:
                for sub_dict in dic.values():
                    sub_dict_return_value = DictUtils.find_sub_dict_by_key(sub_dict, key)

                    if sub_dict_return_value:
                        return sub_dict_return_value
        else:
            return None
