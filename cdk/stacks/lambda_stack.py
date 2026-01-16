from aws_cdk import Stack, Duration, aws_lambda as _lambda, aws_ec2 as ec2
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, lambda_sg: ec2.SecurityGroup, db_secret, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Shared Lambda layer for dependencies
        layer = _lambda.LayerVersion(
            self,
            "DependenciesLayer",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Shared dependencies for Lambda functions",
        )

        # Environment variables - only pass secret ARN, not credentials
        lambda_env = {
            "DB_SECRET_ARN": db_secret.secret_arn,
        }

        # Ingest Lambda function
        self.ingest_function = _lambda.Function(
            self,
            "IngestFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("ingest"),
            layers=[layer],
            environment=lambda_env,
            timeout=Duration.seconds(30),
            memory_size=128,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[lambda_sg],
            allow_public_subnet=True,
        )

        # Query Lambda function
        self.query_function = _lambda.Function(
            self,
            "QueryFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("query"),
            layers=[layer],
            environment=lambda_env,
            timeout=Duration.seconds(30),
            memory_size=128,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[lambda_sg],
            allow_public_subnet=True,
        )

        # Grant secret read permissions (least privilege)
        db_secret.grant_read(self.ingest_function)
        db_secret.grant_read(self.query_function)
