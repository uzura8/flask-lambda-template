#!/bin/bash

k6 run ./vote.js -u 10 -d 10s --rps 15
