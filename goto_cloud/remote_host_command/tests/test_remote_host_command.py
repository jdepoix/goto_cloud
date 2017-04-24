from unittest import TestCase

from ..remote_host_command import RemoteHostCommand


class TestRemoteHostCommand(TestCase):
    def test_render__from_string(self):
        self.assertEquals(
            RemoteHostCommand('ls {FIRSTVAR} {SECONDVAR}').render(firstvar='firstvar', secondvar='secondvar'),
            'ls firstvar secondvar'
        )

    def test_render__from_dict(self):
        self.assertEquals(
            RemoteHostCommand({
                'command': 'ls {OPTIONALS} {FIRSTVAR} {SECONDVAR}',
                'optionals': {
                    'thirdvar': '-3 {THIRDVAR}',
                    'forthvar': '-4 {FORTHVAR}'
                }
            }).render(firstvar='firstvar', secondvar='secondvar', thirdvar='thirdvar', forthvar='forthvar'),
            'ls -3 thirdvar -4 forthvar firstvar secondvar'
        )

    def test_render__with_unused_optionals(self):
        self.assertEquals(
            RemoteHostCommand({
                'command': 'ls {OPTIONALS} {FIRSTVAR} {SECONDVAR}',
                'optionals': {
                    'thirdvar': '-3 {THIRDVAR}',
                    'forthvar': '-4 {FORTHVAR}'
                }
            }).render(firstvar='firstvar', secondvar='secondvar'),
            'ls  firstvar secondvar'
        )

    def test_render__with_partially_used_optionals(self):
        self.assertEquals(
            RemoteHostCommand({
                'command': 'ls {OPTIONALS} {FIRSTVAR} {SECONDVAR}',
                'optionals': {
                    'thirdvar': '-3 {THIRDVAR}',
                    'forthvar': '-4 {FORTHVAR}'
                }
            }).render(firstvar='firstvar', secondvar='secondvar', thirdvar='thirdvar'),
            'ls -3 thirdvar firstvar secondvar'
        )

    def test_render__no_vars(self):
        self.assertEquals(
            RemoteHostCommand('ls').render(),
            'ls'
        )

    def test_render__unused_context(self):
        self.assertEquals(
            RemoteHostCommand({
                'command': 'ls {OPTIONALS} {FIRSTVAR} {SECONDVAR}',
                'optionals': {
                    'thirdvar': '-3 {THIRDVAR}',
                    'forthvar': '-4 {FORTHVAR}'
                }
            }).render(firstvar='firstvar', secondvar='secondvar', fifthvar='fifthvar'),
            'ls  firstvar secondvar'
        )

    def test_render__invalid_context(self):
        with self.assertRaises(RemoteHostCommand.InvalidContextException):
            RemoteHostCommand({
                'command': 'ls {OPTIONALS} {FIRSTVAR} {SECONDVAR}',
                'optionals': {
                    'thirdvar': '-3 {THIRDVAR}',
                    'forthvar': '-4 {FORTHVAR}'
                }
            }).render(firstvar='firstvar'),
