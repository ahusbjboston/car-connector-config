#!/bin/bash

# Interface script to run api test.
# The script is placed here so that in the future if we want to change
# the paramters, we just need the backend repo. No need to touch the 
# devop repo
cd functional_test_cli
bash -c "python3 baft.py"
