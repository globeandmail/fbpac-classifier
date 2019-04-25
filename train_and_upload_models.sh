for langCode in "en-US" "lv-LV" "es-MX" "de-AT" "en-CA" "nl-BE" "da-DK" "en-AU" "en-IE" "it-IT" "de-DE" "fr-CA" "sv-SE" "fi-FI" "de-CH" "nl-NL" "ka-GE"; do
	/usr/local/bin/pipenv run ./classify build --lang $langCode
	aws s3 cp data/$langCode/classifier.dill s3://tgam-fbpac-models/$langCode/classifier.dill
done

