from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_ecs_patterns as ecs_patterns
)

from .database import PostgresDatabase
from .storage import EfsStorage

xwiki_volume_name = "Xwiki_data"


class FargateService(Construct):

    def __init__(self, scope: Construct, id: str, *,
                 cluster: ecs.Cluster,
                 efs_storage: EfsStorage,
                 db: PostgresDatabase):
        super().__init__(scope, id)

        task_definition = self.create_task_definition(efs_storage, db)

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "FargateEcsService",
            cluster=cluster,
            desired_count=1,
            task_definition=task_definition,
            task_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            platform_version=ecs.FargatePlatformVersion.LATEST,
            public_load_balancer=True,
            enable_execute_command=True,
            enable_ecs_managed_tags=True,
        )

        fargate_service.target_group.configure_health_check(
            path="/bin/view/Main/Healthcheck?xpage=plain"
        )

        efs_storage.allow_ecs_access(fargate_service)
        db.allow_ecs_access(fargate_service)

    def create_task_definition(self, efs_storage: EfsStorage, db: PostgresDatabase) -> ecs.FargateTaskDefinition:
        task_definition = ecs.FargateTaskDefinition(
            self, "FargateTaskDefinition",
            cpu=2048,
            memory_limit_mib=4096
        )

        task_definition.add_volume(
            name=xwiki_volume_name,
            efs_volume_configuration=efs_storage.create_ecs_volume_config()
        )

        container = ecs.ContainerDefinition(
            self, "xwiki",
            task_definition=task_definition,
            image=ecs.ContainerImage.from_registry("xwiki:stable-postgres-tomcat"),
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="xwiki",
                log_retention=logs.RetentionDays.ONE_MONTH
            ),
            environment={
                "DB_USER": db.db_user,
                "DB_HOST": db.db_host
            },
            secrets={
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(db.secret, field="password"),
            }
        )

        container.add_mount_points(ecs.MountPoint(
            container_path="/usr/local/xwiki",
            source_volume=xwiki_volume_name,
            read_only=False
        ))

        container.add_port_mappings(ecs.PortMapping(
            container_port=8080,
            protocol=ecs.Protocol.TCP
        ))

        return task_definition
