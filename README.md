# Discord Bot with Azure, Flask, and Terraform

## Table of Contents:
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Azure Setup](#azure-setup)
4. [Terraform Setup](#terraform-setup)
5. [GitHub Actions and Secrets](#github-actions-and-secrets)
6. [Deployment](#deployment)
7. [Post-Deployment Steps](#post-deployment-steps)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

## Introduction
This repository contains a Discord bot that leverages OpenAI's GPT-4, developed in Python and Flask. The bot is containerized using Docker and deployed on Azure Container Instances. This README guides you through setting up and deploying the project.

## Prerequisites
- Python 3.11 or higher
- Flask
- Docker
- Azure CLI
- Terraform
- GitHub account

## Azure Setup
Follow the same steps as outlined previously to install the Azure CLI, sign in to your Azure account, create a resource group, and set up Azure Container Registry.

## Terraform Setup
No changes from the previous setup. Follow the original steps to install and initialize Terraform.

## GitHub Actions and Secrets
Ensure the following secrets are configured in your GitHub repository:
- AZURE_TENANT_ID
- AZURE_CLIENT_ID
- AZURE_CLIENT_SECRET
- AZURE_REGISTRY_USERNAME
- AZURE_REGISTRY_PASSWORD
- OPENAI_API_KEY
- DISCORD_TOKEN

Adjust any steps as necessary for Python and Flask specific configurations.

## Deployment
Deployment via GitHub Actions remains unchanged. Pushing to the 'main' branch triggers the CI/CD pipeline to build the Docker image and deploy it to Azure.

## Post-Deployment Steps
Use Azure CLI commands to verify the container instance is running and fetch logs if needed.

## Troubleshooting
Review Azure container logs and ensure all GitHub Actions Secrets are correctly set for the Python and Flask environment.

## Contributing
Contributions are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for code conduct and pull request guidelines.

## License
This project is licensed under the GNU General Public License v3.0. Developed with assistance from OpenAI's GPT-4 and ChatGPT.