import aws_cdk as core
from aws_cdk.assertions import Match, Template

from cdk_test.cdk_boss_stack import CdkBossStack

app = core.App()
stack = CdkBossStack(app, "cdk-test")
template = Template.from_stack(stack)


def test_basic_rds_properties():
    template.has_resource_properties("AWS::RDS::DBInstance", {
        "DBInstanceClass": Match.string_like_regexp("small$"),
        "DBName": "xwiki",
        "Engine": "postgres",
        "EngineVersion": Match.string_like_regexp("^17"),
        "Port": "5432",
        "PubliclyAccessible": False,
        "StorageType": "gp3"
    })

def test_efs_encrypted():
    template.has_resource_properties("AWS::EFS::FileSystem", {
        "Encrypted": True,
    })
