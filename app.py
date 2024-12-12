#!/usr/bin/env python3
import aws_cdk as cdk

from cdk_test.cdk_boss_stack import CdkBossStack

app = cdk.App()
CdkBossStack(app, "CdkBossStack")

app.synth()
