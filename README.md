# Aerostat

A simple CLI tool to deploy your Machine Learning models to cloud, with public API and template connections ready to go.

## Get started
### Installation
The name `Aerostat` has been used by another PyPI project, please install this package with:
```bash
pip install aerostat-launcher
```
Once installed, it can be used directly via `aerostat`. If it doesn't work, add `python -m` prefix to all commands,
i.e. `python -m aerostat deploy`.

Only three commands needed for deploying your model: `install`, `login`, and `deploy`.

### Setup
1. Run the following command to install all the dependencies needed to run Aerostat. Please allow installation in the pop-up window to
   continue.
```bash
aerostat install
```

2. To login to Aerostat, you need to run the following command:
```bash
aerostat login
```
You will be prompted to choose an existing AWS credentials, or enter a new one. The AWS account used needs to have **AdministratorAccess**.

### Deploy
To deploy your model, you need to dump your model to a file with pickle, and run the following command:
```bash
aerostat deploy
```
You will be prompted to enter:
- the path to your model file
- the input columns of your model
- the ML library used for your model
- the name of your project

Or you can provide these information as command line options like:
```bash
aerostat deploy --model-path /path/to/model --input-columns "['col1','col2','col3']" --python-dependencies scikit-learn --project-name my-project
```

## Connections
Aerostat provides connection templates to use your model in various applications once it is deployed. Currently, it includes templates for:
- Microsoft Excel
- Google Sheets
- Python / Jupyter Notebook

Visit the URL produced by the `aerostat deploy` command to test your model on cloud, and get the connection templates.

## Other Commands
### List
To list all the projects you have deployed, run:
```bash
aerostat ls
```

### Info
To find deployment information of a specific project, such as API endpoint, run:
```bash
aerostat info
```
then choose the project from the list. You can also provide the project name as a command line option like:
```bash
aerostat info my-project
```

## Future Roadmap
- Improve user interface, including rewrite prompts with Rich, use more colors and emojis
- Add unit tests
- Adopt [Semantic Versioning](https://semver.org) once reach v0.1.0 and add
  CI/[CD](https://mestrak.com/blog/semantic-release-with-python-poetry-github-actions-20nn)
- Support SSO login
- Support deploying to GCP