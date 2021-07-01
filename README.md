# Flask + Lambda + APIGateway Template 

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



## Work on local

Execute below command

````bash
python -m flask run
````

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)



## Deploy to Lambda

Execute below command

````bash
serverless deploy --aws-profile your-profile-name
````

Request https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev

