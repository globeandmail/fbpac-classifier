# fbpac-classifier

This is the model and classifier for the [Facebook Political Ad Collector](https://github.com/globeandmail/facebook-political-ads/). For a full breakdown of the other services you'll need to deploy the app, see the [README for our main repo](https://github.com/globeandmail/facebook-political-ads/blob/master/README.md).

We train the model using python and scikit learn. We're using [pipenv](https://docs.pipenv.org/) to track dependencies.

There are two parts to this repo:
- **hourly classifier**: classifies newly-received ads on an hourly basis. It'll classify any ads with a political_probability of exactly `0` — in other words, ads that have never been classified before.
- **weekly model re-trainer**: re-trains the model that classifies future ads based on political/non-political votes received from users.


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

We used to use seeds collceted via the Facebook API to build the model, but that hasn't worked for more than a year. To seed the classifier, provide examples of political ad texts and non-political ad texts, following the formats in data/en-US/seeds.json. You might gather these from Facebook's ad library (if it exists in your country) or from tweets.

Otherwise, building the model now would just on votes in the extension and suppressions in the admin, which would take much, much longer.

To build the classifier you'll want to run:

```sh
pipenv run ./classify build
```

To classify the ads you've collected you can run:

```sh
pipenv run ./classify classify
```

You can download pre-trained models with `pipenv run ./classify get_models`.

### Deployment
