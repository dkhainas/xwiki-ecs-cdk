from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_route53 as route53
)
from constructs import Construct

from cdk_test.xwiki_service import XWikiService


class CdkBossStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self, "EcsVpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name="private_nat", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                ec2.SubnetConfiguration(name="private_isolated", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
            ])

        cluster = ecs.Cluster(
            self, "EcsFargateCluster",
            vpc=vpc
        )

        xwiki = XWikiService(self, id="XWikiService", vpc=vpc, cluster=cluster)
