#aws-dynamodb-sql

This project is me learning DynamoDB with Boto3 on MacOS

What it does?
- Docker-compose file for startin mariadb-server
- Generating a SQL database for lab purpose
- Getting the generated SQL database and mapping data to match my DynamoDB table
- Batch wrighting to DynamoDB

What's missing?
- DynamoDB query error handling
- DynamoDB UnprocessedItems handling


##Prerequisites
 - python3 [Install python3](https://installpython3.com/mac/)
 - docker [Install Docker](https://docs.docker.com/docker-for-mac/install/)
 - docker-compose [Install docker-compose](https://docs.docker.com/compose/install/)
 - aws account [Sign up for aws](https://aws.amazon.com/)
 - aws cli [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html)
 - DynamoDB table [Create DynamoDB Table](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/SampleData.CreateTables.html)
 
 
## Get it running
1. In AWS IAM Console (Web portal), create an IAM user that has AdministratorAccess or limited access to only access DynamoDB.
1. In AWS IAM Console (Web portal), add an Access Key for the user that is used when configuring AWS CLI.
1. Configure the AWS CLI with the Access Key from previous step. [AWS CLI Configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
1. In AWS DynamoDB Console (Web portal), create a dynamodb table with partition key `mail`. If you want the import to go faster. Increase Write capacity units. With 100 units the dynamodb import takes around 40sec. You can decrease it after import.
1. Verify that the DynamoDB table can be accessed from aws cli in mac terminal.
    ```
    aws dynamodb list-tables
    {
        "TableNames": [
            "students"
        ]
    }
    ```
1. create python 3 Virtual environment
    ```
    python3 -m venv .venv
    ```
1. Activate virtual environment
    ```
    source .venv/bin/activate
    ```
1. install requirements
    ```
    pip install -r requirements.txt
    ```
1. modify the [.env](.env) file if you want to make some changes to databases and configuration.
1. start mariadb-server in docker. (this uses the .env file to get credentials)
    ```
    docker-compose up -d
    ```
1. create sql database and NUMBER_OF_STUDENTS ammount fo entries. Inserts in chunks of 500.
    ```
    python3 populate_sql.py
    ```
1. read sql data and send to dynamodb with batch queries of 25.
    ```
    python3 send_sql2ddb.py
    ``` 
