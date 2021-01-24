#!/bin/bash

pipenv run isort . && pipenv run black .

