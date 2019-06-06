# fbpac-classifier

This is the classifier for the [Facebook Political Ad Collector](https://github.com/globeandmail/facebook-political-ads/). For a full breakdown of the other services you'll need to deploy the app, see the [README for our main repo](https://github.com/globeandmail/facebook-political-ads/blob/master/README.md).

We train the classifier using python and scikit learn. We're using [pipenv](https://docs.pipenv.org/) to track dependencies.

There are three parts to the classifier:
- **hourly classifier**: classifies newly-received ads on an hourly basis. It'll classify any ads with a political_probability of exactly `0`.
- **daily classifier**:
- **weekly classifier**:


### Installation

To download pipenv, use [homebrew](https://brew.sh/):
```sh
brew install pipenv
```

To get started you can run:

```sh
pipenv install
pipenv shell
```

To download the seeds for the classifier, you'll need a Facebook app with the proper permissions and you'll run the seed command like this:

```sh
FACEBOOK_APP_ID=whatever FACEBOOK_APP_SECRET=whatever DATABASE_URL=postgres://whatever/facebook_ads ./classify seed en-US
```

Alternatively, you can build the model without seeds, relying instead just on votes in the extension and suppressions in the admin. And to build the classifier you'll want to run:

```sh
pipenv run ./classify build
```

To classify the ads you've collected you can run:

```sh
pipenv run ./classify classify
```

You can download pre-trained models with `pipenv run ./classify get_models`.

### Deployment
