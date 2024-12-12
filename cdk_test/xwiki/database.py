from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    aws_ecs_patterns as ecs_patterns,
    RemovalPolicy
)

postgres_port = 5432


class PostgresDatabase(Construct):

    def __init__(self, scope: Construct, id: str, *, vpc: ec2.Vpc, db_name: str) -> None:
        super().__init__(scope, id)

        instance_type = ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL)
        engine_version = rds.PostgresEngineVersion.VER_17_2

        self.db = rds.DatabaseInstance(self, "PostgresDb",
                                       database_name=db_name,
                                       engine=rds.DatabaseInstanceEngine.postgres(version=engine_version),
                                       instance_type=instance_type,
                                       storage_type=rds.StorageType.GP3,
                                       vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                                       vpc=vpc,
                                       port=postgres_port,
                                       removal_policy=RemovalPolicy.DESTROY,
                                       deletion_protection=False)

        self.db_host: str = self.db.instance_endpoint.hostname
        self.db_user: str = "postgres"
        self.secret: secretsmanager.Secret = self.db.secret
        self.password_arn: str = self.db.secret.secret_arn

    def allow_ecs_access(self, service: ecs_patterns.ApplicationLoadBalancedFargateService) -> None:
        service.service.connections.allow_from(self.db, ec2.Port.tcp(postgres_port))
        service.service.connections.allow_to(self.db, ec2.Port.tcp(postgres_port))
