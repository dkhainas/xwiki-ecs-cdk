import aws_cdk as core
from aws_cdk.assertions import Match, Template

from cdk_test.cdk_boss_stack import CdkBossStack

app = core.App()
stack = CdkBossStack(app, "cdk-test")
template = Template.from_stack(stack)


def test_basic_vpc_properties():
    template.has_resource_properties("AWS::EC2::VPC", {
        "CidrBlock": "10.0.0.0/16",
        "EnableDnsHostnames": True,
        "EnableDnsSupport": True,
    })


def test_vpc_multi_az():
    # Subnets allocated in different AZs
    subnets = template.find_resources("AWS::EC2::Subnet")
    availability_zones = {
        subnet["Properties"]["AvailabilityZone"]["Fn::Select"][0]
        for subnet in subnets.values()
    }
    assert len(availability_zones) > 1

    # Nats associated with different subnets
    nats = template.find_resources("AWS::EC2::NatGateway")
    nat_subnets = {
        nat["Properties"]["SubnetId"]["Ref"]
        for nat in nats.values()
    }
    assert len(nat_subnets) > 1


def test_vpc_has_private_subnets():
    template.has_resource_properties("AWS::EC2::Subnet", {
        "MapPublicIpOnLaunch": False
    })


def test_multiple_sg_used_no_default():
    # rds + efs + ecs + elb
    template.resource_count_is("AWS::EC2::SecurityGroup", 4)
