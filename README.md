# AI-Powered Product Listing Optimiser

> **Live Demo:** [main.dr87o9j4s7beg.amplifyapp.com](https://main.dr87o9j4s7beg.amplifyapp.com/)

An event-driven, serverless AWS pipeline that automatically rewrites and scores Amazon product listings using generative AI. Upload a raw product CSV, watch each listing optimise in real time, and download a file ready to upload straight to Amazon Seller Central.

Built by [Sheldon De Souza](https://www.linkedin.com/in/sheldon-desouza/) — transitioning from 6 years in eCommerce operations into AWS Cloud and AI Engineering.

---

## Screenshots

### Upload your CSV
![Upload page](assets/screenshot-upload.png)

### Real-time progress — each product ticks off as Bedrock processes it
![Progress](assets/screenshot-progress.png)

### Complete — 10 products, 92/100 average score, 49 seconds
![Complete](assets/screenshot-complete.png)

### Before: raw product data
![Before](assets/screenshot-before.png)

### After: AI-optimised titles, bullet points, descriptions and scores
![After](assets/screenshot-after.png)

---

## The Problem

Writing high-quality Amazon listings is time-consuming and inconsistent. Most sellers do it manually or pay expensive copywriters. Poor listings directly impact search ranking, click-through rate, and conversion.

This project automates the entire process using AWS-native AI services, and is grounded in real eCommerce experience working with brands like Veloforte and V12 Footwear.

---

## Architecture

```
+-----------------------------------------------------------------+
|                          AWS Cloud                              |
|                                                                 |
|  Website         API Gateway       Orchestrator Lambda          |
|  (Amplify) ────► POST /optimise ──► Creates job in DynamoDB    |
|                                     Triggers Processor async    |
|                  Returns job ID ◄── Returns 202 instantly      |
|                                                                 |
|  Website polls   API Gateway       Orchestrator Lambda          |
|  every 3s  ────► GET ?job_id=x ──► Reads DynamoDB status       |
|                  Returns progress ◄ Returns % complete          |
|                                                                 |
|                                    Processor Lambda             |
|                                    Calls Bedrock per product    |
|                                    Updates DynamoDB progress    |
|                                    Writes output CSV to S3      |
|                                    Sends SNS notification       |
+-----------------------------------------------------------------+
```

### Why async?

API Gateway has a hard 29-second timeout. Processing 10 products through Bedrock takes 45-60 seconds. The async pattern solves this: the website gets a job ID back in under 1 second, then polls for real-time progress while the Processor Lambda runs in the background with no timeout pressure.

---

## Services Used

| Service | Role |
|---|---|
| Amazon S3 | Input CSV storage, output CSV storage, event trigger |
| AWS Lambda x2 (Python 3.12) | Orchestrator returns job ID instantly; Processor runs async |
| Amazon Bedrock (Claude 3 Haiku) | Rewrites titles, bullets, descriptions and scores each listing |
| Amazon DynamoDB | Tracks job status and real-time progress |
| Amazon API Gateway | REST API with CORS for the website |
| Amazon SNS | Email notification on job completion |
| AWS Amplify | Hosts the frontend website |
| AWS CloudFormation | Full infrastructure as code, single template deployment |
| AWS IAM | Least privilege roles and policies |
| Amazon CloudWatch | Lambda logs and monitoring |

---

## What Gets Optimised

Each product is rewritten to meet Amazon best practices for search visibility (A9/Rufus algorithm):

| Field | Before | After |
|---|---|---|
| Title | `Nike running shoe mens` | `Nike Air Max 270 Men's Running Shoe, Lightweight Breathable Mesh, Max Air Cushioning` |
| Bullet 1 | `Good for running` | `SUPERIOR CUSHIONING: Large Max Air unit delivers all-day comfort and impact absorption` |
| Description | `Lightweight shoe` | `Engineered for performance and everyday style, the Nike Air Max 270...` |
| Score | — | `92/100 with improvement notes` |

---

## Live Demo

Visit [main.dr87o9j4s7beg.amplifyapp.com](https://main.dr87o9j4s7beg.amplifyapp.com/) and upload the included `sample-products.csv` to see it in action.

---

## Deploy Your Own

### Prerequisites

- AWS account with Bedrock enabled
- AWS CLI installed and configured
- Git

### Step 1: Clone the repo

```bash
git clone https://github.com/Sheldon-desouza/ai-product-listing-optimiser.git
cd ai-product-listing-optimiser
```

### Step 2: Deploy the CloudFormation stack

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name listing-optimiser \
  --parameter-overrides \
      ProjectName=listing-optimiser \
      NotificationEmail=your-email@example.com \
      BedrockModelId=anthropic.claude-3-haiku-20240307-v1:0 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-2
```

### Step 3: Get your API URL

```bash
aws cloudformation describe-stacks \
  --stack-name listing-optimiser \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
  --output text \
  --region eu-west-2
```

### Step 4: Update index.html with your API URL, push to GitHub, connect to Amplify.

---

## Input CSV Format

```csv
asin,title,description,brand,category,price
B09B8YWXTS,Instant Pot Duo 7-in-1,Multi cooker...,Instant Pot,Kitchen Appliances,79.99
```

Required: `title`, `description`, `brand`, `category`. Optional: `asin`, `price`

---

## Output CSV Columns Added

| Column | Description |
|---|---|
| `optimised_title` | Keyword-rich title, max 200 chars |
| `bullet_1` to `bullet_5` | Benefit-led bullet points |
| `optimised_description` | Full listing description |
| `listing_score` | Quality score out of 100 |
| `score_notes` | AI improvement notes |

---

## Cost Estimate (10 products)

| Service | Cost |
|---|---|
| Lambda, DynamoDB, SNS, API Gateway | ~$0.00 (free tier) |
| S3 | ~$0.01 |
| Bedrock Claude 3 Haiku | ~$0.05-$0.20 |
| **Total** | **Under $0.25** |

---

## Roadmap

- [x] Async architecture with DynamoDB job tracking
- [x] Real-time progress bar with per-product updates
- [x] Live website on AWS Amplify
- [ ] Amazon Rekognition to score product images
- [ ] Multi-marketplace mode (Amazon, Shopify, eBay)
- [ ] RAG pipeline using brand guidelines as context
- [ ] LLM evaluation dashboard

---

## About

Built as part of the AWS re/Start Cloud Engineering Programme (Cohort GBLON18).

**Skills demonstrated:** Async serverless architecture, CloudFormation IaC, Lambda (Python), Amazon Bedrock, DynamoDB, API Gateway, AWS Amplify, IAM least privilege, CloudWatch observability.

---

## Author

**Sheldon De Souza** — AWS Cloud & AI Engineer (in Training) | eCommerce Technology Specialist

[LinkedIn](https://www.linkedin.com/in/sheldon-desouza/) · [GitHub](https://github.com/Sheldon-desouza)
