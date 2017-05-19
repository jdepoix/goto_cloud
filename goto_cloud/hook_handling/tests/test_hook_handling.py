from unittest import TestCase
from unittest.mock import patch

from remote_host.public import RemoteHost

from source.public import Source

from target.public import Target

from test_assets.public import TestAsset

from ..hook_handling import HookEventHandler


class TestHookHandling(TestCase, metaclass=TestAsset.PatchRemoteHostMeta):
    TEST_HOOKS = {
        'GET_TARGET_SYSTEM_INFORMATION_AFTER': {
            'location': 'TARGET',
            'execute': 'GET_TARGET_SYSTEM_INFORMATION_AFTER',
        },
        'GET_TARGET_SYSTEM_INFORMATION_BEFORE': {
            'location': 'SOURCE',
            'execute': 'GET_TARGET_SYSTEM_INFORMATION_BEFORE',
        }
    }

    def setUp(self):
        self.source = Source.objects.create(
            remote_host=RemoteHost.objects.create(address='ubuntu16'),
            target=Target.objects.create(
                remote_host=RemoteHost.objects.create(address='target__device_identification'),
                blueprint={
                    'hooks': self.TEST_HOOKS
                }
            )
        )

        self.triggered_script = None
        self.execution_location = None
        self.execution_env = None

        self.hook_event_handler = HookEventHandler(self.source)

    def get_mocked_script_execution_decorator(self):
        def mocked_script_execution(remote_script_executor, script, env=None):
            self.triggered_script = script
            self.execution_location = remote_script_executor.remote_executor.remote_host.address
            self.execution_env = env
        return mocked_script_execution

    def test_emit__no_hook_triggered(self):
        with patch(
            'remote_script_execution.remote_script_execution.RemoteScriptExecutor.execute',
            self.get_mocked_script_execution_decorator()
        ):
            self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)

            self.assertIsNone(self.triggered_script)

    def test_emit(self):
        with patch(
            'remote_script_execution.remote_script_execution.RemoteScriptExecutor.execute',
            self.get_mocked_script_execution_decorator()
        ):
            self.source.increment_status()
            self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)

            self.assertEqual(self.triggered_script, 'GET_TARGET_SYSTEM_INFORMATION_BEFORE')

            self.hook_event_handler.emit(HookEventHandler.EventType.AFTER)

            self.assertEqual(self.triggered_script, 'GET_TARGET_SYSTEM_INFORMATION_AFTER')

    def test_emit__executed_in_correct_location(self):
        with patch(
            'remote_script_execution.remote_script_execution.RemoteScriptExecutor.execute',
            self.get_mocked_script_execution_decorator()
        ):
            self.source.increment_status()
            self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)

            self.assertEqual(self.execution_location, 'ubuntu16')

            self.hook_event_handler.emit(HookEventHandler.EventType.AFTER)

            self.assertEqual(self.execution_location, 'target__device_identification')

    def test_emit__env_loaded(self):
        with patch(
            'remote_script_execution.remote_script_execution.RemoteScriptExecutor.execute',
            self.get_mocked_script_execution_decorator()
        ):
            self.source.increment_status()
            self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)

            self.assertDictEqual(self.execution_env, {
                'blueprint': self.source.target.blueprint,
                'device_mapping': self.source.target.device_mapping,
                'source_system_info': self.source.remote_host.system_info,
                'target_system_info': self.source.target.remote_host.system_info
            })


    def test_emit__env_loaded_without_target_remote_host(self):
        with patch(
            'remote_script_execution.remote_script_execution.RemoteScriptExecutor.execute',
            self.get_mocked_script_execution_decorator()
        ):
            self.source.target.remote_host = None
            self.source.target.save()
            self.source.increment_status()
            self.hook_event_handler.emit(HookEventHandler.EventType.BEFORE)

            self.assertDictEqual(self.execution_env, {
                'blueprint': self.source.target.blueprint,
                'device_mapping': self.source.target.device_mapping,
                'source_system_info': self.source.remote_host.system_info,
                'target_system_info': {}
            })
