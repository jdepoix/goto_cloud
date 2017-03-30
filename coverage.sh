#!/usr/bin/env bash

virtualenv/bin/coverage run manage.py test && virtualenv/bin/coverage report
