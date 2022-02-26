## Notify AWS Billing Cost via LINE Notify

LINE Notify version of the following.

[AWSサービス毎の請求額を毎日Slackに通知してみた | DevelopersIO](https://dev.classmethod.jp/articles/notify-slack-aws-billing/)

## Setup

1. Install AWS CLI

1. Generate LINE Notify Token
   [LINE Notify](https://notify-bot.line.me/my/)

1. Install sam CLI

1. Create S3 Bucket
    ```bash
    $ aws s3 mb s3://[Bucket Name]
    ```
1. Build
    ```bash
    $ sam build
    ```
1. Upload package to s3
    ```bash
    $ sam package \
      --output-template-file packaged.yaml \
      --s3-bucket [Bucket Name]
    ```

1. Deploy
    ```bash
    $ am deploy --template-file packaged.yaml \
      --stack-name [Stack Name] \
      --capabilities CAPABILITY_IAM \
      --parameter-overrides LineNotifyToken=[LINE Notify Token]
    ```
