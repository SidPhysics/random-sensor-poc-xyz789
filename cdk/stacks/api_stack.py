from aws_cdk import Stack, aws_apigateway as apigw, aws_lambda as _lambda
from constructs import Construct

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, ingest_function: _lambda.Function, query_function: _lambda.Function, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # REST API Gateway
        api = apigw.RestApi(
            self,
            "WeatherSensorAPI",
            rest_api_name="Weather Sensor Metrics API",
            description="API for ingesting and querying weather sensor metrics",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
        )

        # /metrics endpoint for ingest
        metrics = api.root.add_resource("metrics")
        metrics.add_method(
            "POST",
            apigw.LambdaIntegration(ingest_function),
        )

        # /query endpoint for query
        query = api.root.add_resource("query")
        query.add_method(
            "GET",
            apigw.LambdaIntegration(query_function),
        )

        self.api = api
