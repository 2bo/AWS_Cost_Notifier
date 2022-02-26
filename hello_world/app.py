import json
import boto3
import os
import requests
import typing
from datetime import datetime, timedelta, date

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def lambda_handler(event, context) -> None:
    # cost explorer client
    client = boto3.client('ce', region_name = 'us-east-1')

    total_billing = get_total_billing(client)
    service_billings = get_service_billings(client)

    (title, detail) = get_message(total_billing, service_billings)
    post_slack(title, detail)

    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

def get_total_billing(client) -> dict:
    (start_date, end_date) = get_total_cost_date_range()

    response = client.get_cost_and_usage(
        TimePeriod = {
            'Start': start_date,
            'End': end_date
        },
        Granularity = 'MONTHLY',
        Metrics = [
            'AmortizedCost',
        ]
    )

    return {
        'start': response['ResultByTime'][0]['TimePeriod']['Start'],
        'end': response['ResultsByTime'][0]['TimePeriod']['End'],
        'billing': response['ResultsByTime'][0]['Total']['AmortizedCost']['Amount']
    }

def get_service_billings(client) -> list;
    (start_date, end_date) = get_total_cost_date_range()

    response = client.get_cost_and_usage(
        TimePeriod = {
            'Start': start_date,
            'End': end_date
        },
        Granularity = 'MONTHLY',
        Metrics=[
            'AmortizedCost'
        ],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key':'SERVICE'
            }
        ]
    )

    billings = []

    for item in response['ResultsByTime'][0]['Groups']:
        billings.append({
            'service_name': item['Keys'][0],
            'billing': item['Metrics']['AmortizedCost']['Amount']
        })
    return billings


def get_message(total_billing: dict, service_billings: list) -> (str, str):
    start = datetime.strptime(total_billing['start'], '%Y-%m-%d').strftime('%m/%d')

    end_today = datetime.strptime(total_billing['end'], '%Y-%m-%d')
    end_yesterday = (end_today - timedelta(days=1)).strftime('%m/%d')

    total = round(float(total_billing['billing']), 2)

    title = f'{start}〜{end_yesterday}の請求額は、{total:.2f} USDです。'

    details = []
    for item in service_billings:
        service_name = item['service_name']
        billing = round(float(item['billing']), 2)

        if billing == 0.0:
            continue
        details.append(f' ・{service_name}: {billing:.2f} USD')

    return title, '\n'.join(details)

def post_slack(title: str, detail: str) -> None:
    payload = {
        'attachments': [
            {
                'color': '#36a64f',
                'pretext': title,
                'text': detail
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, date=json.dumps(payload))
    except requests.exceptions.RequestException as e:
        print(e)
    else:
        print(response.status_code)

def get_total_cost_date_range() -> typing.Tuple[str, str]:
    start_date = get_begin_of_month()
    end_date = get_today()

    if start_date == end_date:
        end_of_month = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=-1)
        begin_of_month = end_of_month.replace(day=1)
        return begin_of_month.date().isoformat(), end_date
    return start_date, end_date

def get_begin_of_month() -> str:
    return date.today().replace(day=1).isoformat()

def get_prev_day(prev: int) -> str:
    return (date.today() - timedelta(days=prev)).isoformat()

def get_today() -> str:
    return date.today().isoformat()
