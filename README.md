# Serverless-CMS

Constructed by

* Serverside:
    + Flask + Lambda + APIGateway (deploy by Serverless Framework)
    + DynamoDB
* Frontend: VueJS

## Instration


#### Preparation

You need below

* nodeJS >= v14.15.X
* aws-cli >= 1.18.X
* Terraform >= 0.14.5

#### Install tools

Install serverless, python venv and terraform on mac

```bash
# At project root dir
npm install -g serverless
python3 -m venv .venv

brew install tfenv
tfenv install 0.14.5
tfenv use 0.14.5
```

### Install Packages

Install npm packages

```bash
# At project root dir
npm install
```

Install python packages

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

#### Use Contact component

If use Contact component, execute bellow

```bash
. .venv/bin/activate
pip install -r pytz Flask-WTF
```

## Deploy AWS Resources by Terraform

#### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Buckets like below in ap-northeast-1 region

* __your-serverless-deployment__
    + Store deployment state files by terraformand and serverless framework
    + Create directory "terraform/your-project-name"
* __your-serverless-configs__
    + Store config files for app
    + Create directory "your-project-name/frontend/prd" and "your-project-name/frontend/dev"

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

```terraform
prj_prefix = "your-porject-name"
 ...
route53_zone_id        = "Set your route53 zone id"
domain_api_prd         = "your-domain-api.example.com"
domain_api_dev         = "your-domain-api-dev.example.com"
domain_static_site_prd = "your-domain-static.example.com"
domain_static_site_dev = "your-domain-static-dev.example.com"
domain_media_site_prd  = "your-domain-media.example.com"
domain_media_site_dev  = "your-domain-media-dev.example.com"
```

#### 2. Set AWS profile name to environment variable

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

#### 3. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=your-deployment" -backend-config="key=terraform/your-project/terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

#### 5. Create Admin User

Create Admin User by aws-cli

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_DEFAULT_REGION="ap-northeast-1"

aws cognito-idp admin-create-user \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--username your-username \
--user-attributes \
  Name=email,Value=sample@example.com \
  Name=email_verified,Value=True \
  Name=custom:role,Value=admin \
  Name=custom:acceptServiceIds,Value=hoge \
--desired-delivery-mediums EMAIL
```

You get temporary password by email
Update password as parmanent

```bash
aws cognito-idp admin-set-user-password \
--user-pool-id ap-northeast-1_xxxxxxxxx \
--username your-username \
--password 'your-parmanent-password' \
--permanent
```

#### 6. Set CORS of media file bucket

* Access to S3 console of media file bucket
* Select tab "Permission"
* Press "Edit" button of  "Cross-origin resource sharing (CORS)"
* Set bellow

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "DELETE",
            "GET"
        ],
        "AllowedOrigins": [
            "https://your-domain.example.com"
        ],
        "ExposeHeaders": []
    }
]
```

## DynamoDB Backup Settings

If you want to backup DynamoDB items, set bellows

* Access to "AWS Backup" on AWS Console and set region
* Press "Create backup plan"
* Input as follows for "Plan"
    + Start options
        - Select "Build a new plan"
        - Backup plan name: your-project-dynamodb-backup
    + Backup rule configuration
        - Backup vault: Default
        - Backup rule name: your-project-dynamodb-backup-rule
        - Backup frequency: Daily
        - Backup window: Customize backup window
        - Backup window settings: as you like
    + Press "Create backup plan"
* Input as follows for "Assign resources"
    + General
        - Resource assignment name: your-project-dynamodb-backup-assignment
        - IAM role: Default role
    + Resource selection
        - 1. Define resource selection: Include specific resource types
        - 2. Select specific resource types: DynamoDB
            - Table names: All tables
        - 4. Refine selection using tags
            - Key: backup
            - Condition for value: Eauqls
            - Value: aws-backup
    + Press "Assign resources"

## Deploy Server Side Resources

### Setup configs

Setup config files per stage

```bash
cp -r config/stages-sample config/stages
vi config/stages/*
```

```bash
# config/stages/common.yml

service: 'your-project-name'
awsAccountId: 'your-aws-acconnt-id'
defaultRegion: 'ap-northeast-1'
deploymentBucketName: 'your-serverless-deployment'
 ...
```

```bash
# config/stages/prd.yml
# config/stages/dev.yml

domainName: your-domain-api.example.com
corsAcceptOrigins: 'https://your-domain.example.com'
notificationEmail: admin@example.com
 ...
mediaS3BucketName: "your-domain-media.example.com"
 ...
commentImportS3BucketName: "your-content-resources"
commentImportS3BucketPath: "your-project/prd/comments"
 ...
```


### Create Domains for API

Execute below command

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

sls create_domain # Deploy for dev
```

If deploy for prod

```bash
sls create_domain --stage prd # Deploy for prod
```

### Deploy to Lambda

Execute below command

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

sls deploy # Deploy for dev
```

If deploy for prod

```bash
sls deploy --stage prd # Deploy for prod
```

### Save default ServiceId on DynamoDB

1. Open DynamoDB page on AWS console
2. Click Tables > Explore items
3. Select "your-prefix-stage-service"
4. Click "Create item"
5. Select "JSON"
6. Input below, and create

```bash
{
  "serviceId": {
    "S": "hoge"
  },
  "label": {
    "S": "ほげ"
  }
}
````

## Deploy Frontend Resources
### Setup about TinyMCE Editor
* Access to [TinyMCE Dashbord](https://www.tiny.cloud/my-account/dashboard/)
* Get Your Tiny API Key
* Move to [Approved Domains](https://www.tiny.cloud/my-account/domains/), then Add your static-site domain

### Set enviroment variables

* Access to https://github.com/{your-account}/{repository-name}/settings/secrets/actions
* Push "New repository secret"
* Add Below
    * Common
        * __AWS_ACCESS_KEY_ID__ : your-aws-access_key
        * __AWS_SECRET_ACCESS_KEY__ : your-aws-secret_key
    * For Production
        * __CLOUDFRONT_DISTRIBUTION__ : your cloudfront distribution created by terraform for production
        * __S3_CONFIG_BUCKET__: "your-serverles-configs/your-project/frontend/prd" for production
        * __S3_RESOURCE_BUCKET__: "your-domain-static-site.example.com" for production
    * For Develop
        * __CLOUDFRONT_DISTRIBUTION_DEV__ : your cloudfront distribution created by terraform for develop
        * __S3_CONFIG_BUCKET_DEV__: "your-serverles-configs/your-project/frontend/dev" for develop
        * __S3_RESOURCE_BUCKET_DEV__: "your-domain-static-site-dev.example.com" for develop

### Upload config file for frontend app

#### Edit config file
#### Basic config

```bash
cd (project_root_dir)
cp src/client/js/config/config.json.sample src/client/js/config/config.json
vi src/client/js/config/config.json
```

```json
{
  "domain": "your-domain-api.example.com",
  "port": null,
  "baseUrl": "/",
  "isSSL": true,
 ...
  "media": {
    "url": "https://your-domain-media.example.com",
 ...
  },
  "tinyMCEApiKey": "your-tinyMCE-api-key"
}
```

#### AWS Cognito config (If use admin functions)

```bash
cp src/client/js/config/cognito-client-config.json.sample src/client/js/config/cognito-client-config.json
vi src/client/js/config/cognito-client-config.json
```

```json
{
  "Region": "ap-northeast-1",
  "UserPoolId": "ap-northeast-1_xxxxxxxxx",
  "ClientId": "xxxxxxxxxxxxxxxxxxxxxxxxxx",
  "IdentityPoolId": "ap-northeast-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

#### Upload S3 Bucket "your-serverless-configs/your-project-name/frontend/{stage}"

#### Deploy continually on pushed to git


## Development
### Local Development

Install packages for development

```bash
. .venv/bin/activate
pip install pylint
```

### Work on local

Set venv

```bash
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

### Convert existing DB records to DynamoDB

Install packages for converter if use MySQL for convert target service

```bash
. .venv/bin/activate
pip install PyMySQL
```

Set converter of target service

```bash
cd (root/)develop/db_converter/services/
git clone {repository url of target service converter}
```

Execute converter

```bash
cd (root/)develop/db_converter
python main.py {service_name}
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
sls delete_domain --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com" 

Destroy for static server resources by Terraform

```bash
terraform destroy -auto-approve -var-file=./terraform.tfvars
```

