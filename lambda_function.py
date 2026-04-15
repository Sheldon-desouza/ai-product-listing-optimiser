import json
import csv
import boto3
import os
import logging
import io
import base64
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')
sns = boto3.client('sns')

OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def optimise_listing(product):
    prompt = f"""You are an expert Amazon listing copywriter.
Optimise the following product listing for Amazon search (Rufus/A9 algorithm).

Return ONLY valid JSON with these exact fields:
- optimised_title (max 200 chars, keyword-rich)
- bullet_1 through bullet_5 (benefit-led, max 255 chars each)
- optimised_description (max 2000 chars, paragraph form)
- listing_score (integer 0-100)
- score_notes (brief improvement notes)

Product data:
Title: {product.get('title', '')}
Description: {product.get('description', '')}
Brand: {product.get('brand', '')}
Category: {product.get('category', '')}
Price: {product.get('price', '')}
ASIN: {product.get('asin', '')}

Return only the JSON object, no markdown, no preamble."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    })

    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType='application/json',
        accept='application/json'
    )

    result = json.loads(response['body'].read())
    text = result['content'][0]['text']
    return json.loads(text)

def process_products(products):
    results = []
    total = len(products)
    for i, product in enumerate(products):
        logger.info(f"Optimising product {i+1}/{total}: {product.get('title','')[:50]}")
        try:
            optimised = optimise_listing(product)
            results.append({**product, **optimised})
        except Exception as e:
            logger.error(f"Failed to optimise product {i+1}: {str(e)}")
            results.append({
                **product,
                'optimised_title': 'ERROR - could not optimise',
                'bullet_1': str(e),
                'bullet_2': '', 'bullet_3': '', 'bullet_4': '', 'bullet_5': '',
                'optimised_description': '',
                'listing_score': 0,
                'score_notes': 'Processing failed'
            })
    return results

def write_output_csv(results, filename):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_key = f"optimised/{timestamp}-{filename}"
    output_buffer = io.StringIO()
    fieldnames = list(results[0].keys())
    writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
    s3.put_object(
        Bucket=OUTPUT_BUCKET,
        Key=output_key,
        Body=output_buffer.getvalue().encode('utf-8'),
        ContentType='text/csv'
    )
    return output_key

def generate_presigned_url(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': OUTPUT_BUCKET, 'Key': key},
        ExpiresIn=3600
    )

def handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    # API Gateway request (website upload)
    if event.get('httpMethod') == 'POST':
        try:
            body = event.get('body', '')
            if event.get('isBase64Encoded'):
                body = base64.b64decode(body).decode('utf-8')

            # Parse the multipart or raw CSV
            # Expect raw CSV in body for simplicity
            reader = csv.DictReader(io.StringIO(body))
            products = list(reader)

            if not products:
                return {
                    'statusCode': 400,
                    'headers': CORS_HEADERS,
                    'body': json.dumps({'error': 'No products found in CSV'})
                }

            logger.info(f"API request: processing {len(products)} products")
            results = process_products(products)
            output_key = write_output_csv(results, 'web-upload.csv')
            download_url = generate_presigned_url(output_key)

            # Build summary for frontend
            scores = [r.get('listing_score', 0) for r in results if isinstance(r.get('listing_score'), int)]
            avg_score = round(sum(scores) / len(scores)) if scores else 0

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'success': True,
                    'products_processed': len(results),
                    'average_score': avg_score,
                    'download_url': download_url,
                    'preview': [
                        {
                            'original_title': r.get('title', ''),
                            'optimised_title': r.get('optimised_title', ''),
                            'listing_score': r.get('listing_score', 0),
                            'score_notes': r.get('score_notes', '')
                        }
                        for r in results[:3]
                    ]
                })
            }

        except Exception as e:
            logger.error(f"API error: {str(e)}")
            return {
                'statusCode': 500,
                'headers': CORS_HEADERS,
                'body': json.dumps({'error': str(e)})
            }

    # S3 trigger (original flow)
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        logger.info(f"S3 trigger: processing s3://{bucket}/{key}")
        obj = s3.get_object(Bucket=bucket, Key=key)
        content = obj['Body'].read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        products = list(reader)
        results = process_products(products)
        if results:
            output_key = write_output_csv(results, key.split('/')[-1])
            logger.info(f"Output written to s3://{OUTPUT_BUCKET}/{output_key}")
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject='Product Listing Optimiser - Complete',
                Message=f"Optimised {len(results)} products.\nOutput: s3://{OUTPUT_BUCKET}/{output_key}"
            )

    return {'statusCode': 200, 'body': 'Complete'}
