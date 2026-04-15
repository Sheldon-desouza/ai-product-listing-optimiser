# AI-Powered Product Listing Optimiser
## Deployment Guide

---

## Prerequisites

Before deploying, check these three things:

1. AWS CLI installed and configured (`aws configure`)
2. Bedrock access enabled in your AWS account:
   - Go to AWS Console > Bedrock > Model Access
   - Enable: Claude 3 Sonnet
3. SES email verified (if using SES notifications):
   - For now the stack uses SNS email subscription which is simpler

---

## Step 1 - Deploy the CloudFormation Stack

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name listing-optimiser \
  --parameter-overrides \
      ProjectName=listing-optimiser \
      NotificationEmail=your-email@example.com \
      BedrockModelId=anthropic.claude-3-sonnet-20240229-v1:0 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region eu-west-2
```

Note: Use eu-west-2 (London) as your region. Check Bedrock is available there,
if not use us-east-1 and update your region accordingly.

---

## Step 2 - Confirm SNS Email Subscription

After deploying you will receive an email from AWS SNS asking you to confirm
your subscription. Click Confirm Subscription before testing.

---

## Step 3 - Get Your Bucket Names

```bash
aws cloudformation describe-stacks \
  --stack-name listing-optimiser \
  --query "Stacks[0].Outputs" \
  --output table
```

This prints your input and output bucket names.

---

## Step 4 - Upload a Test CSV

```bash
aws s3 cp sample-products.csv s3://listing-optimiser-input-YOUR_ACCOUNT_ID/
```

Replace YOUR_ACCOUNT_ID with your actual AWS account number.

---

## Step 5 - Watch it Run

Open CloudWatch Logs to see the Lambda in action:

```bash
aws logs tail /aws/lambda/listing-optimiser-optimiser --follow
```

---

## Step 6 - Download Optimised Output

```bash
aws s3 ls s3://listing-optimiser-output-YOUR_ACCOUNT_ID/optimised/
aws s3 cp s3://listing-optimiser-output-YOUR_ACCOUNT_ID/optimised/YOUR_FILE.csv .
```

---

## Expected Output CSV Columns

Your output CSV will contain all original columns plus:

| Column | Description |
|---|---|
| optimised_title | Keyword-rich title up to 200 chars |
| bullet_1 to bullet_5 | Benefit-led bullet points |
| optimised_description | Full Amazon description |
| listing_score | Quality score out of 100 |
| score_notes | Notes on what was improved |

---

## Tear Down (to avoid charges)

```bash
# Empty buckets first (required before deleting stack)
aws s3 rm s3://listing-optimiser-input-YOUR_ACCOUNT_ID --recursive
aws s3 rm s3://listing-optimiser-output-YOUR_ACCOUNT_ID --recursive

# Delete the stack
aws cloudformation delete-stack --stack-name listing-optimiser
```

---

## Cost Estimate (light usage)

| Service | Estimated Cost |
|---|---|
| Lambda (100 invocations) | ~$0.00 (free tier) |
| S3 storage | ~$0.01 |
| Bedrock Claude Sonnet (100 products) | ~$0.50 |
| SNS | ~$0.00 (free tier) |
| CloudWatch Logs | ~$0.01 |

Total: under $1 for testing.
