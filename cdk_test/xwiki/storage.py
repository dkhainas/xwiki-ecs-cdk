from constructs import Construct
from aws_cdk import (
    aws_efs as efs,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    RemovalPolicy,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
)

efs_port = 2049


class EfsStorage(Construct):

    def __init__(self, scope: Construct, id: str, *, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id)

        self.file_system = efs.FileSystem(
            self, "EfsStorage",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.access_point = efs.AccessPoint(
            self, "EfsStorageAccessPoint",
            file_system=self.file_system
        )

    def create_ecs_volume_config(self) -> ecs.EfsVolumeConfiguration:
        ecs.EfsVolumeConfiguration(
            file_system_id=self.file_system.file_system_id,
            authorization_config=ecs.AuthorizationConfig(
                access_point_id=self.access_point.access_point_id,
                iam="ENABLED"
            ),
            transit_encryption="ENABLED"
        )

    def allow_ecs_access(self, service: ecs_patterns.ApplicationLoadBalancedFargateService) -> None:
        # Open Security Group for NFS port
        service.service.connections.allow_from(self.file_system, ec2.Port.tcp(efs_port))
        service.service.connections.allow_to(self.file_system, ec2.Port.tcp(efs_port))

        # Allow ECS Agent to list, mount and read/write the EFS volume
        service.task_definition.execution_role.add_to_policy(
            iam.PolicyStatement(actions=["elasticfilesystem:DescribeFileSystems"], effect=iam.Effect.ALLOW,
                                resources=["*"]))
        self.file_system.grant_root_access(service.task_definition.execution_role)
        self.file_system.grant(service.task_definition.execution_role, "elasticfilesystem:DescribeMountTargets")
