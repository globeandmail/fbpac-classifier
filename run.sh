#!/bin/bash

# This can be used to run both the hourly and weekly training sessions
#
# To run weekly, set the WEEKLY environment variable to true
#
# To process all ads in the hourly training, set the EVERY environment variable to true

if [ "$WEEKLY" == "true" ]
then
echo "Running weekly training"
for langCode in "en-US" "lv-LV" "es-MX" "de-AT" "en-CA" \
                "nl-BE" "da-DK" "en-AU" "en-IE" "it-IT" \
                "de-DE" "fr-CA" "sv-SE" "fi-FI" "de-CH" \
                "nl-NL" "ka-GE"
do
echo "Running weekly training for $langCode"
./classify build --lang $langCode | tee -a /tmp/model_build.log
done
./upload_trained_models.py
else
    if [ "$EVERY" == "true" ]
    then
    echo "Running hourly training for all ads"
    ./classify get_models && \
    ./classify classify --every && \
    ./classify entities && \
    ./classify listbuilding_fundraising_classify
    else
    echo "Running hourly training"
    ./classify get_models && \
    ./classify classify && \
    ./classify entities && \
    ./classify listbuilding_fundraising_classify
    fi
fi