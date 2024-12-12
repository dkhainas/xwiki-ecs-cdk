from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs
)

from cdk_test.xwiki.database import PostgresDatabase
from cdk_test.xwiki.fargate_service import FargateService
from cdk_test.xwiki.storage import EfsStorage


class XWikiService(Construct):

    def __init__(self, scope: Construct, id: str, *, vpc: ec2.Vpc, cluster: ecs.Cluster) -> None:
        super().__init__(scope, id)

        db = PostgresDatabase(self, id="XWikiDb", vpc=vpc, db_name="xwiki")
        storage = EfsStorage(self, id="XWikiStorage", vpc=vpc)
        service = FargateService(self, id="XWikiService", cluster=cluster, efs_storage=storage, db=db)
