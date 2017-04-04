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

    @staticmethod
    def merge_dicts(dominant_dict, other_dict):
        """
        returns a new dict which contains a merge of the given dicts. If there are key collisions, the first given dict
        overwrites the values, of the second dict. In case of both values belonging to the collision keys, are dicts
        too, these are merged as well.
        same.
        
        :param dominant_dict: the dominant dict
        :type dominant_dict: dict
        :param other_dict: the other dict
        :type other_dict: dict
        :return: merged dict
        :rtype: dict
        """
        dominant_dict_keys = dominant_dict.keys()
        other_dict_keys = other_dict.keys()
        common_keys = dominant_dict_keys & other_dict_keys

        merged_dict = {
            **DictUtils.filter_dict(other_dict, other_dict_keys - common_keys),
            **DictUtils.filter_dict(dominant_dict, dominant_dict_keys - common_keys),
        }

        for common_key in common_keys:
            if isinstance(dominant_dict[common_key], dict) and isinstance(other_dict[common_key], dict):
                merged_dict[common_key] = DictUtils.merge_dicts(dominant_dict[common_key], other_dict[common_key])
            else:
                merged_dict[common_key] = dominant_dict[common_key]

        return merged_dict

    @staticmethod
    def filter_dict(target_dict, keys):
        """
        filters a dict, by a given set of keys
        
        :param target_dict: the dict to filter
        :type target_dict: dict
        :param keys: the keys to filter for
        :type keys: list or tuple or set
        :return: filtered dict
        :rtype: dict
        """
        return {key: target_dict[key] for key in keys}
