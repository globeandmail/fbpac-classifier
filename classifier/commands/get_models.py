"""
Downloads existing classifiers
"""
import click
import boto3
from classifier.utilities import confs
from subprocess import call

s3 = boto3.client("s3")


@click.option("--lang", help="Limit to language")
@click.command("get_models")
@click.pass_context
def get_models(ctx, lang):
    """
    download classifiers for each of our languages.
    """
    for (directory, conf) in confs(ctx.obj["base"]):
        if lang and conf["language"] != lang:
            continue
        model_path = "data/{}/classifier.dill".format(conf["language"])
        classifier_file = "{}/classifier.dill".format(conf["language"])
        # call(["wget", "-nv", "-O", model_path, "https://s3.amazonaws.com/pp-data/fbpac-models/{}/classifier.dill".format(conf["language"])])
        print("Fetching " + classifier_file + " from S3")
        s3.download_file("tgam-fbpac-models", classifier_file, model_path)
