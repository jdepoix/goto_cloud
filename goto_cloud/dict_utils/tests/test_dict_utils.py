from unittest import TestCase

from ..dict_utils import DictUtils


TEST_TREE_DICT = {
    '0': {},
    '1': {
        '2': {
            '3': '4'
        },
        '5': {
            '6': '7',
            '8': '9'
        }
    },
    '10': {
        '11': {
            '12': {
                '13': '14',
                '21': {},
                '22': {
                    '23': {
                        '24': '25'
                    },
                    '26': '27'
                },
                '15': '16',
            }
        },
        '17': {
            '18': {
                '19': '20'
            }
        }
    }
}


class TestDictUtils(TestCase):
    def test_flatten_child_elements(self):
        self.assertEqual(
            set(DictUtils.flatten_child_elements(TEST_TREE_DICT)),
            set([str(i) for i in range(28)])
        )

    def test_find_sub_dict_by_key(self):
        self.assertDictEqual(
            DictUtils.find_sub_dict_by_key(TEST_TREE_DICT, '11'),
            {
                '12': {
                    '13': '14',
                    '21': {},
                    '22': {
                        '23': {
                            '24': '25'
                        },
                        '26': '27'
                    },
                    '15': '16',
                }
            }
        )

    def test_find_sub_dict_by_key__not_found(self):
        self.assertIsNone(DictUtils.find_sub_dict_by_key(TEST_TREE_DICT, '999'))

    def test_merge_dicts(self):
        self.assertEqual(
            DictUtils.merge_dicts(
                {
                    '0': {
                        '1': '2'
                    },
                    '1': {
                        '2': {
                            '4': '5'
                        },
                        '5': None
                    },
                    '10': {
                        '11': {
                            '13': {}
                        },
                        '17': '13'
                    }
                },
                TEST_TREE_DICT,
            ),
            {
                '0': {
                    '1': '2'
                },
                '1': {
                    '2': {
                        '3': '4',
                        '4': '5'
                    },
                    '5': None
                },
                '10': {
                    '11': {
                        '12': {
                            '13': '14',
                            '21': {},
                            '22': {
                                '23': {
                                    '24': '25'
                                },
                                '26': '27'
                            },
                            '15': '16',
                        },
                        '13': {}
                    },
                    '17': '13'
                }
            }
        )

    def test_get_values(self):
        self.assertEquals(
            DictUtils.filter_dict(
                {
                    '1': 1,
                    '2': 2,
                    '3': {
                        '1': 1,
                        '2': 2,
                    },
                    '4': 4,
                    '5': 5,
                },
                ['2', '3', '5']
            ),
            {'2': 2, '3': {'1': 1,'2': 2,}, '5': 5}
        )
