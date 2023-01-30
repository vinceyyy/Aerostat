# Aerostat

Aerostat is a simple CLI tool to deploy your Machine Learning models to cloud, with a public API to use.

## Get started
### Installation
The name `Aerostat` has been used by another PyPI project, please install this package with:
```bash
pip install git+https://github.com/vinceyyyyyy/Aerostat
```
Most likely you will need to run this module with `python -m` prefix since it is not included in `$PATH`.

To deploy your model, there are only three commands needed: `install`, `login`, and `deploy`.

### Setup
Run the following command, and it will install all the dependencies needed to run Aerostat.
```bash
python -m aerostat install
```

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

Or you can provide these information as command line options like:
```bash
python -m aerostat deploy --model-path /path/to/model --input-columns "['col1','col2','col3']" --python-dependencies scikit-learn
```


## Roadmap
- [x] Deploy a model to AWS Lambda
- [ ] Improve error handling, including login checks
- [ ] Improve user interface, including rewrite prompts with Rich, use more colors and emojis
- [ ] Return deployment info and simple test demo with HTTP GET request
- [ ] Make it a pip installable package
- [ ] Handle AWS authentication from the CLI
- [ ] Support deploying to GCP