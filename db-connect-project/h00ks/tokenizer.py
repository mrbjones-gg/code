#!/usr/bin/env python3
"""
Simple AWS S3 tokenizer: lists objects in a bucket/prefix and tokenizes text objects.
Usage: python tokenizer.py --bucket my-bucket [--prefix folder/] [--profile default]

This script uses boto3 and standard AWS credential chain (env vars, shared-credentials, IAM role).
Do NOT hardcode credentials in code.
"""

import argparse
import logging
import re
from collections import Counter
import boto3
import botocore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"\b\w+\b")


def get_session(profile=None, region=None):
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)


def list_s3_keys(s3_client, bucket, prefix=None, max_keys=1000):
    paginator = s3_client.get_paginator("list_objects_v2")
    pagination_params = {"Bucket": bucket}
    if prefix:
        pagination_params["Prefix"] = prefix

    for page in paginator.paginate(**pagination_params):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def fetch_text_object(s3_client, bucket, key):
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()
        # try decode as utf-8
        return body.decode("utf-8", errors="replace")
    except botocore.exceptions.ClientError as e:
        logger.warning("Failed to fetch %s: %s", key, e)
        return None


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


def main():
    parser = argparse.ArgumentParser(description="Tokenize text objects from S3")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument("--prefix", help="S3 prefix to filter objects")
    parser.add_argument("--profile", help="AWS CLI profile name to use")
    parser.add_argument("--region", help="AWS region (optional)")
    parser.add_argument("--max", type=int, default=10, help="Max number of objects to process")
    args = parser.parse_args()

    session = get_session(profile=args.profile, region=args.region)
    s3 = session.client("s3")

    logger.info("Listing objects in s3://%s/%s", args.bucket, args.prefix or "")
    count = 0
    global_counter = Counter()

    for key in list_s3_keys(s3, args.bucket, prefix=args.prefix):
        if count >= args.max:
            break
        # simple heuristic: only process .txt or common text-like keys
        if not (key.lower().endswith(".txt") or key.lower().endswith(".csv") or key.lower().endswith(".log")):
            # still attempt but skip binary-like files by extension
            logger.debug("Skipping non-text-looking key: %s", key)
            continue

        logger.info("Fetching %s", key)
        text = fetch_text_object(s3, args.bucket, key)
        if text is None:
            continue
        tokens = tokenize(text)
        global_counter.update(tokens)
        logger.info("%s: %d tokens", key, len(tokens))
        count += 1

    # print top tokens
    if global_counter:
        logger.info("Top tokens overall:")
        for token, freq in global_counter.most_common(20):
            print(f"{token}: {freq}")
    else:
        logger.info("No tokens collected. Check bucket/prefix and object types.")


if __name__ == "__main__":
    main()
