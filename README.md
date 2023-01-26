# Aerostat

Aerostat is a simple CLI tool to deploy your Machine Learning models to cloud, with a public API to use.

## Get started
This project hasn't been build as a standalone package yet, so you need to clone the repository and run it through python.

To deploy your model, there are only three commands needed: `install`, `login`, and `deploy`.

### Install
Run the following command, and it will install all the dependencies needed to run Aerostat.
```bash
python -m aerostat install
```

### Login
To login to Aerostat, you need to run the following command:
```bash
python -m aerostat login
```
You will be prompted to choose an existing AWS credentials, or enter a new one. The AWS account used needs to have **AdministratorAccess**. 

### Deploy
To deploy your model, you need to dump your model to a file with pickle, and run the following command:
```bash
python -m aerostat deploy
```
You will be prompted to enter:
- the path to your model file
- the input columns of your model
- the ML library used for your model

## Roadmap
- [x] Deploy a model to AWS Lambda
- [ ] Capture the API endpoint generated, even when no change deployed
- [ ] Improve error handling, including login checks
- [ ] Improve user interface, including rewrite prompts with Rich, use more colors and emojis
- [ ] Return deployment info and simple test demo with HTTP GET request
- [ ] Make it a pip installable package
- [ ] Handle AWS authentication from the CLI
- [ ] Support deploying to GCP