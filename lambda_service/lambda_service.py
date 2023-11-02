from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_event_sources,
    aws_iam as iam,
    aws_ec2 as ec2,
    Duration
)
from constructs import Construct


class LambdaService(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        private_subnet_configuration = ec2.SubnetConfiguration(
            name='lambda-private-subnet-1',
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
            cidr_mask=24,
        )
        public_subnet_configuration = ec2.SubnetConfiguration(
            name='lambda-public-subnet-1',
            subnet_type=ec2.SubnetType.PUBLIC,
            cidr_mask=24,
        )

        vpc = ec2.Vpc(
            self, "LambdaVPC",
            cidr='10.0.0.0/16',
            nat_gateways=1,
            max_azs=3,
            subnet_configuration=[private_subnet_configuration, public_subnet_configuration],
        )

        queue = sqs.Queue(
            self, "LambdaServiceSQS",
            queue_name="LambdaServiceSQS.fifo",
            visibility_timeout=Duration.seconds(300),
            fifo=True
        )

        handler4 = lambda_.Function(
            self, "SQSHandler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("resources"),
            handler="sqs_handler.lambda_handler",
            vpc=vpc,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
        )

        event_source = lambda_event_sources.SqsEventSource(queue)
        handler4.add_event_source(event_source)

        # lambda function to send a message to SQS queue
        handler3 = lambda_.Function(
            self, "SendSQSMessage",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("resources"),
            handler="send_sqs_message.lambda_handler",
            environment={
                "SQS_QUEUE_URL": queue.queue_url
            },
            vpc=vpc,
            vpc_subnets={
                "subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
        )
        handler3.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[queue.queue_arn],
            actions=["*"]
        ))

        post_send_sqs_message = apigateway.LambdaIntegration(
            handler3,
            request_templates={
                "application/json": '{ "statusCode": "200" }'
            }
        )

        api = apigateway.RestApi(
            self, "lambda-apis",
            rest_api_name="Lambda Service",
            description="This service serves lambda apis."
        )

        send_sqs_message = api.root.add_resource("sqs_message")
        send_sqs_message.add_method("POST", post_send_sqs_message)  # POST /sqs_message
