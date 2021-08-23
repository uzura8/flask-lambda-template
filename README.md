# Flask + Lambda + APIGateway Template 

This document refered to https://www.serverless.com/blog/flask-python-rest-api-serverless-lambda-dynamodb

## Instration

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
cp -r config-sample config
vi config/{stg-name}.yml
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

````bash
sls wsgi serve
````

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)



## Deploy to Lambda

Execute below command

````bash
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"
sls deploy # Deploy for dev
````

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



### Performance Test

#### Setup K6

Install for macOS

```bash
brew install k6
```

#### Execute

```
k6 run ./dev_tools/performance/vote.js --vus NN --duration MMs
```

