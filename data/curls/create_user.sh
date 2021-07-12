#!/bin/bash

curl -H "Content-Type: application/json" -X POST http://localhost:5000/users -d '{"userId": "alexdebrie1", "name": "Alex DeBrie"}'

