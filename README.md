# AWS Lambda Automation Project

## Project Overview
This project automates file uploads and downloads using Python and AWS services.

## Features
- Upload files to Amazon S3.
- Download files from Amazon S3.
- Generate CSV reports.
- Automate file-processing tasks using Python.
- Track upload and download results.

## Technologies Used
- Python
- Amazon Web Services (AWS)
- Amazon S3
- Boto3
- Git and GitHub

## Project Files
- `main.py` — Main Python application.
- `requirements.txt` — Python dependencies.
- `sample.txt` — Sample input file.
- `automatic_upload_report.csv` — Upload report.
- `downloaded_report.csv` — Download report.
- `s3_upload_report.csv` — S3 upload report.

## Prerequisites
- Python 3
- An AWS account
- AWS CLI configured with appropriate permissions

## Installation
Install the required Python dependency:

```bash
pip install -r requirements.txt
```

## AWS Configuration
Configure AWS credentials securely using an AWS CLI profile or an IAM role. Never hardcode access keys or secret keys in the source code.

## Running the Project
Run:

```bash
python main.py
```

## Security
Do not commit AWS credentials, passwords, private keys, or sensitive report data to GitHub.