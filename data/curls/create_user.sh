#!/bin/bash

curl -H "Content-Type: application/json" -X POST http://localhost:5000/users -d '{"userId": "taroyamada", "name": "Taro Yamada"}'

