#!/usr/bin/env python

import boto3
from datetime import datetime
import os

s3 = boto3.client("s3")

Bucket = "tgam-fbpac-models"

dirs = [
    "en-US",
    "lv-LV",
    "es-MX",
    "de-AT",
    "en-CA",
    "nl-BE",
    "da-DK",
    "en-AU",
    "en-IE",
    "it-IT",
    "de-DE",
    "fr-CA",
    "sv-SE",
    "fi-FI",
    "de-CH",
    "nl-NL",
    "ka-GE",
]

filename = "classifier.dill"

for lang in dirs:
    Filename = f"data/{lang}/{filename}"
    Key = f"weekly/{lang}/{filename}"
    exists = os.path.isfile(Filename)
    if exists:
        print(f"Uploading {Key} to S3")
        s3.upload_file(Filename, Bucket, Key)
    else:
        print(f"{Filename} not found")
    
date = datetime.today().strftime('%Y-%m-%d')

logfile = "model_build.log"
local_filename = f"/tmp/{logfile}"
upload_filename = f"model_build_{date}.log"
print(f"Uploading {upload_filename} to S3")
s3.upload_file(local_filename, Bucket, upload_filename)
