from aws_cdk import Stack, aws_apigateway as apigw, aws_lambda as _lambda
from constructs import Construct


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        ingest_function: _lambda.Function,
        query_function: _lambda.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # REST API Gateway
        api = apigw.RestApi(
            self,
            "WeatherSensorAPI",
            rest_api_name="Weather Sensor Metrics API",
            description="API for ingesting and querying weather sensor metrics",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=1000,  # Global limit (higher than per-client)
                throttling_burst_limit=2000,
            ),
        )

        # Usage Plan for per-client rate limiting
        usage_plan = api.add_usage_plan(
            "WeatherSensorUsagePlan",
            name="Weather Sensor API Usage Plan",
            description="100 requests per client with burst of 50",
            throttle=apigw.ThrottleSettings(
                rate_limit=100,  # 100 requests per second per client
                burst_limit=50,  # Burst of 50 requests
            ),
            quota=apigw.QuotaSettings(
                limit=10000,  # 10,000 requests per month per client
                period=apigw.Period.MONTH,
            ),
        )

        # API Key for client identification (optional - can be used without keys)
        api_key = api.add_api_key(
            "WeatherSensorAPIKey",
            api_key_name="weather-sensor-default-key",
            description="Default API key for weather sensor API",
        )

        # Associate API key with usage plan
        usage_plan.add_api_key(api_key)

        # /metrics endpoint for ingest
        metrics = api.root.add_resource("metrics")
        metrics.add_method(
            "POST",
            apigw.LambdaIntegration(ingest_function),
            api_key_required=False,  # Can be accessed without API key
        )

        # /query endpoint for query
        query = api.root.add_resource("query")
        query.add_method(
            "GET",
            apigw.LambdaIntegration(query_function),
            api_key_required=False,  # Can be accessed without API key
        )

        self.api = api
