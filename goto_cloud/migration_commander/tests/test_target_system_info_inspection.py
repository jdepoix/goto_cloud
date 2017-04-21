from django.test import TestCase

from test_assets.public import TestAsset

from source.public import Source

from remote_host.public import RemoteHost

from target.public import Target

from ..target_system_info_inspection import GetTargetSystemInfoCommand


class TestGetTargetSystemInfoCommand(TestCase, metaclass=TestAsset.PatchRemoteHostMeta):
    def setUp(self):
        remote_host = RemoteHost.objects.create(address='ubuntu12')
        self.source = Source.objects.create(remote_host=remote_host)
        self.source.target = Target.objects.create(remote_host=remote_host)

    def test_execute(self):
        GetTargetSystemInfoCommand(self.source).execute()
        self.assertEquals(
            self.source.target.remote_host.system_info,
            TestAsset.REMOTE_HOST_MOCKS['ubuntu12'].get_config()
        )
