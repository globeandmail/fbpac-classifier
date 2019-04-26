#!/bin/bash
echo "running get_models"
./classify get_models && \
./classify classify && \
./classify entities && \
./classify listbuilding_fundraising_classify