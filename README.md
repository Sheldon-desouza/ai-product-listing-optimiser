# AI-Powered Product Listing Optimiser

An event-driven, serverless AWS pipeline that automatically rewrites and scores Amazon product listings using generative AI. Upload a raw product CSV, get back an optimised listing file ready to upload to Amazon Seller Central.

Built by Sheldon De Souza — transitioning from 6 years in eCommerce operations into AWS Cloud and AI Engineering.

---

## The Problem

Writing high-quality Amazon listings is time-consuming and inconsistent. Most sellers either do it manually or pay expensive copywriters. Poor listings directly impact search ranking, click-through rate, and conversion.

This project automates the entire process using AWS-native AI services.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                │
│                                                                 │
│  CSV Upload          Lambda            Amazon Bedrock           │
│  ──────────►  S3  ──────────► Parse ──────────► Claude AI      │
│  (Input      (Trigger)        CSV     (Rewrite     │            │
│   Bucket)                             listings)    │            │
│                                                    ▼            │
│                                              Optimised          │
│                                              Listings           │
│                                                    │            │
│              SNS Email  ◄──────  S3  ◄────────────┘            │
│              Notification       (Output                         │
│                                  Bucket)                        │
│                                                                 │
│              CloudWatch Logs ◄── Lambda (monitoring)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Services Used

| Service | Role |
|---|---|
| Amazon S3 | Input and output storage, event trigger |
| AWS Lambda (Python 3.12) | Orchestrates the pipeline |
| Amazon Bedrock (Claude 3 Sonnet) | Rewrites and scores listings |
| Amazon SNS | Email notification on completion |
| AWS CloudFormation | Full infrastructure as code |
| AWS IAM | Least privilege roles and policies |
| Amazon CloudWatch | Logging and monitoring |

---

## What Gets Optimised

Each product is rewritten to meet Amazon's best practices for search visibility (A9/Rufus algorithm):

| Field | Before | After |
|---|---|---|
| Title | `Nike running shoe mens` | `Nike Air Max 270 Men's Running Shoe, Lightweight Breathable Mesh, Max Air Cushioning, Sizes 7-13` |
| Bullet 1 | `Good for running` | `SUPERIOR CUSHIONING: Large Max Air unit in the heel delivers all-day comfort and impact absorption for runners and casual wear` |
| Description | `Lightweight shoe` | `Engineered for performance and everyday style, the Nike Air Max 270...` |
| Listing Score | — | `78/100 with improvement notes` |

---

## Prerequisites

1. AWS account with Bedrock access enabled
2. Claude 3 Sonnet model enabled in Bedrock console (Model Access)
3. AWS CLI installed and configured
4. Python 3.12+

---

## Deploy in 3 Steps

**Step 1: Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/ai-product-listing-optimiser.git
cd ai-product-listing-optimiser
```

**Step 2: Deploy the CloudFormation stack**
```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name listing-optimiser \
  --parameter-overrides \
      ProjectName=listing-optimiser \
      NotificationEmail=your-email@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-2
```

**Step 3: Upload a product CSV**
```bash
aws s3 cp sample-products.csv s3://listing-optimiser-input-YOUR_ACCOUNT_ID/
```

The pipeline runs automatically. Check your email for the optimised file link.

---

## Input CSV Format

```csv
asin,title,description,brand,category,price
B09B8YWXTS,Instant Pot Duo 7-in-1,Multi cooker...,Instant Pot,Kitchen Appliances,79.99
```

Required columns: `title`, `description`, `brand`, `category`
Optional columns: `asin`, `price`

---

## Output CSV

All original columns are preserved. These columns are added:

| Column | Description |
|---|---|
| `optimised_title` | Keyword-rich title, max 200 chars |
| `bullet_1` to `bullet_5` | Benefit-led bullet points, max 255 chars each |
| `optimised_description` | Full listing description, max 2000 chars |
| `listing_score` | Quality score out of 100 |
| `score_notes` | AI-generated improvement notes |

---

## Monitoring

View Lambda logs in real time:
```bash
aws logs tail /aws/lambda/listing-optimiser-optimiser --follow
```

---

## Cost Estimate

For a typical test run of 10-20 products:

| Service | Estimated Cost |
|---|---|
| Lambda | ~$0.00 (within free tier) |
| S3 | ~$0.01 |
| Bedrock Claude 3 Sonnet | ~$0.10-$0.50 |
| SNS | ~$0.00 (within free tier) |
| **Total** | **Under $1** |

---

## Tear Down

```bash
aws s3 rm s3://listing-optimiser-input-YOUR_ACCOUNT_ID --recursive
aws s3 rm s3://listing-optimiser-output-YOUR_ACCOUNT_ID --recursive
aws cloudformation delete-stack --stack-name listing-optimiser
```

---

## Roadmap

- [ ] DynamoDB table for listing score history and trends
- [ ] Amplify front end for CSV upload via browser
- [ ] Amazon Rekognition to score product images alongside text
- [ ] Multi-marketplace mode (Amazon UK, Amazon US, Shopify, eBay)
- [ ] RAG integration using brand guidelines as context

---

## About

Built as part of the AWS re/Start Cloud Engineering Programme (Cohort GBLON18) to demonstrate real-world AI and cloud engineering skills grounded in eCommerce domain expertise.

**Skills demonstrated:** CloudFormation IaC, Lambda (Python), Bedrock generative AI, event-driven architecture, IAM least privilege, S3 lifecycle management, CloudWatch observability.

---

## Author

**Sheldon De Souza**
AWS Cloud & AI Engineer (in Training) | eCommerce Technology Specialist
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) | [GitHub](https://github.com/YOUR_USERNAME)
