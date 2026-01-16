from aws_cdk import Stack, aws_ec2 as ec2, aws_rds as rds, RemovalPolicy
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda security group (created here to avoid circular dependency)
        self.lambda_sg = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=vpc,
            description="Security group for Lambda functions",
            allow_all_outbound=True,
        )

        # Security group for RDS
        self.db_security_group = ec2.SecurityGroup(
            self,
            "DBSecurityGroup",
            vpc=vpc,
            description="Security group for RDS PostgreSQL",
            allow_all_outbound=True,
        )

        # Allow Lambda to connect to RDS
        self.db_security_group.add_ingress_rule(
            peer=self.lambda_sg,
            connection=ec2.Port.tcp(5432),
            description="Allow Lambda to connect to RDS",
        )

        # RDS PostgreSQL (free tier: db.t3.micro, 20GB storage, single-AZ)
        # Public subnet with publicly_accessible=True (Lambda outside VPC)
        self.db_instance = rds.DatabaseInstance(
            self,
            "WeatherSensorDB",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[self.db_security_group],
            allocated_storage=20,
            max_allocated_storage=20,
            multi_az=False,
            publicly_accessible=True,  # Required for Lambda outside VPC
            database_name="weathersensor",
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False,
        )

        self.db_secret = self.db_instance.secret
