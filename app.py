#!/usr/bin/env python3
import os
from aws_cdk import App, Environment

from cdk.stacks.network_stack import NetworkStack
from cdk.stacks.database_stack import DatabaseStack
from cdk.stacks.lambda_stack import LambdaStack
from cdk.stacks.api_stack import ApiStack

app = App()

env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1"),
)

project_name = "weather-sensor-poc"

network_stack = NetworkStack(app, f"{project_name}-network", env=env)

database_stack = DatabaseStack(
    app,
    f"{project_name}-database",
    vpc=network_stack.vpc,
    env=env,
)

lambda_stack = LambdaStack(
    app,
    f"{project_name}-lambda",
    db_secret=database_stack.db_secret,
    env=env,
)

api_stack = ApiStack(
    app,
    f"{project_name}-api",
    ingest_function=lambda_stack.ingest_function,
    query_function=lambda_stack.query_function,
    env=env,
)

app.synth()
