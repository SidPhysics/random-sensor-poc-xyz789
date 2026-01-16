from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC without NAT Gateway (free tier compliant)
        self.vpc = ec2.Vpc(
            self,
            "WeatherSensorVPC",
            max_azs=2,
            nat_gateways=0,  # No NAT Gateway to avoid $32/month cost
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )
