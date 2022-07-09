# Flask + Lambda + APIGateway Template 

This document refered to https://www.serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb

## Instration

#### Preparation

You need below

* nodeJS >= v14.15.X
* aws-cli >= 1.18.X

#### Install Serverless Framework

```bash
npm install -g serverless
```

### Install Packages

Install npm packages

```bash
# At project root dir
npm install
```

Install python packages

```bash
pip install -r requirement.txt
```

Setup config files per stage

```bash
cp -r config/stages-sample config/stages
cp -r config/contact/sample config/contact/your-service-id
vi config/stages-sample/*
vi config/contact/your-service-ida/*
```



## Work on local

Setup venv

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Start dynamodb local

```bash
sls dynamodb install
sls dynamodb start
```

Execute below command

```bash
sls wsgi serve
```

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)


#### Execute Script

```bash
sls invoke local --function funcName --data param
```

## Deploy AWS Resources by Terraform

#### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Bucket named "content-api-config-hoge"

#### Preparation

You need below

* aws-cli >= 1.18.X
* Terraform >= 0.14.5

##### Example Installation Terraform by tfenv on mac

```bash
brew install tfenv
tfenv install 0.14.5
tfenv use 0.14.5
```

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

```terraform
 ...
route53_zone_id = "Set your route53 zone id"
domain_api_dev  = "your-domain-api-dev.example.com"
domain_api_prd  = "your-domain-api.example.com"
```

#### 2. Set AWS profile name to environment variable

```bash
export AWS_PROFILE=your-aws-profile-name
export AWS_DEFAULT_REGION="ap-northeast-1"
```

#### 3. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=content-api-config-hoge" -backend-config="key=terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

#### 5. Create Admin User

Create Admin User on Cognito consele

#### 6. Change User Status

```bash
aws cognito-idp admin-initiate-auth \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--client-id xxxxxxxxxxxxxxxxxxxxxxxxxx \
--auth-flow ADMIN_USER_PASSWORD_AUTH \
--auth-parameters \
USERNAME=********,PASSWORD=*********

# Response
{
    "ChallengeName": "NEW_PASSWORD_REQUIRED",
    "Session": "xxxxx....", # Copy this value
    ...
}

aws cognito-idp admin-respond-to-auth-challenge \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--client-id xxxxxxxxxxxxxxxxxxxxxxxxxx \
--challenge-name NEW_PASSWORD_REQUIRED \
--challenge-responses NEW_PASSWORD='your-password',USERNAME=your-username \
--session "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

```

#### 7. Set Admin Role for user

```bash
aws cognito-idp admin-update-user-attributes \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--username your-user-name \
--user-attributes Name="custom:role",Value="admin"
```

#### 8. Sign In by Admin User

Access to https://your-domain.example.com/admin , and Sign In by created user.

## Create Domains for API

Execute below command

```bash
export AWS_PROFILE="your-profile-name"
export AWS_REGION="us-east-1"
sls create_domain # Deploy for dev
```

If deploy for prod

```bash
sls create_domain --stage prd # Deploy for prod
```


## Deploy to Lambda

Execute below command

```bash
export AWS_PROFILE="your-profile-name"
export AWS_REGION="us-east-1"
sls deploy # Deploy for dev
```

If deploy for prod

```bash
sls deploy --stage prd # Deploy for prod
```

Request https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev



## Development

### Execute Backup task on local

```bash
serverless invoke local --function backupVoteLog
```

### Truncate Comemnt Table

```bash
serverless invoke --function commentTruncater --stage dev
```


### Performance Test

#### Setup K6

Install for macOS

```bash
brew install k6
```

#### Execute

```bash
k6 run ./dev_tools/performance/vote.js --vus NN --duration MMs
```


## Destroy Resources

Destroy for serverless resources

```bash
sls remove --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com" 

Destroy for static server resources by Terraform

```bash
terraform destroy -auto-approve -var-file=./terraform.tfvars
```

