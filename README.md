# Discord Bot with Azure and Terraform

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
This repository contains a Discord bot that leverages OpenAI's GPT-4. The bot is containerized using Docker and deployed on Azure Container Instances. This README provides a step-by-step guide to get you up and running.

## Prerequisites
- Node.js v20 or higher
- Docker
- Azure CLI
- Terraform
- GitHub account

## Azure Setup
1. Install Azure CLI: [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. Run `az login` to sign in to your Azure account.
3. Create a resource group: `az group create --name <ResourceGroupName> --location <Location>`
4. Create Azure Container Registry: `az acr create --resource-group <ResourceGroupName> --name <RegistryName> --sku Basic`

## Terraform Setup
1. Install Terraform: [https://learn.hashicorp.com/tutorials/terraform/install-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)
2. Initialize Terraform: `terraform init`
3. Validate the configuration: `terraform validate`
4. Apply the configuration: `terraform apply`

## GitHub Actions and Secrets
1. Go to your GitHub repo -> Settings -> Secrets.
2. Add the following secrets:
  - AZURE_TENANT_ID
  - AZURE_CLIENT_ID
  - AZURE_CLIENT_SECRET
  - AZURE_REGISTRY_USERNAME
  - AZURE_REGISTRY_PASSWORD_1
  - OPENAI_API_KEY
  - DISCORD_TOKEN

## Deployment
1. Push to the 'main' branch.
2. GitHub Actions will automatically build the Docker image and deploy it to Azure.

## Post-Deployment Steps
1. Verify the container instance is running: `az container show --name <ContainerName> --resource-group <ResourceGroupName>`
2. Fetch logs if needed: `az container logs --name <ContainerName> --resource-group <ResourceGroupName>`

## Troubleshooting
- Check Azure logs: `az container logs --name <ContainerName> --resource-group <ResourceGroupName>`
- Make sure GitHub Actions Secrets are correctly set.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for details on code conduct and the pull request process.

## License
This project is licensed under the GNU General Public License v3.0. Developed with assistance from OpenAI's GPT-4 and ChatGPT.