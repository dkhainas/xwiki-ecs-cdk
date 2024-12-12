import aws_cdk as core
from aws_cdk.assertions import Match, Template

from cdk_test.cdk_boss_stack import CdkBossStack

app = core.App()
stack = CdkBossStack(app, "cdk-test")
template = Template.from_stack(stack)

# def test_https_setup():
#     template.has_resource_properties("AWS::CertificateManager::Certificate", {
#         "DomainName": Match.string_like_regexp("example.org$")
#     })
#
#     template.has_resource_properties("AWS::ElasticLoadBalancingV2::Listener", {
#         "Port": 443,
#         "Protocol": "HTTPS"
#     })
#
#     # HTTP to HTTPS redirect setup
#     template.has_resource_properties("AWS::ElasticLoadBalancingV2::Listener", {
#         "Port": 80,
#         "Protocol": "HTTP",
#         "DefaultActions": [{
#             "RedirectConfig": {
#                 "Port": "443",
#                 "Protocol": "HTTPS",
#                 "StatusCode": "HTTP_301"
#             },
#             "Type": "redirect"
#         }]
#     })
