# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
from typing import List, Optional

_HTTP_SCHEMA: str = "http://"
_HTTPS_SCHEMA: str = "https://"


class SqsUrlParser:
    @staticmethod
    def get_queue_name(url: str) -> Optional[str]:
        """
        Best-effort logic to extract queue name from an HTTP url. This method should only be used with a string that is,
        with reasonably high confidence, an SQS queue URL. Handles new/legacy/some custom URLs. Essentially, we require
        that the URL should have exactly three parts, delimited by /'s (excluding schema), the second part should be a
        12-digit account id, and the third part should be a valid queue name, per SQS naming conventions.
        """
        if url is None:
            return None
        url = url.replace(_HTTP_SCHEMA, "").replace(_HTTPS_SCHEMA, "")
        split_url: List[Optional[str]] = url.split("/")
        if len(split_url) == 3 and _is_account_id(split_url[1]) and _is_valid_queue_name(split_url[2]):
            return split_url[2]
        return None

    @staticmethod
    def get_account_id(url: str) -> Optional[str]:
        """
        Extracts the account ID from an SQS URL.
        """
        if url is None:
            return None
        url = url.replace(_HTTP_SCHEMA, "").replace(_HTTPS_SCHEMA, "")
        split_url: List[Optional[str]] = url.split("/")
        if _is_valid_sqs_url(url):
            return split_url[1]
        return None

    @staticmethod
    def get_region(url: str) -> Optional[str]:
        """
        Extracts the region from an SQS URL.
        """
        if url is None:
            return None
        url = url.replace(_HTTP_SCHEMA, "").replace(_HTTPS_SCHEMA, "")
        split_url: List[Optional[str]] = url.split("/")
        if _is_valid_sqs_url(url):
            domain: str = split_url[0]
            domain_parts: List[str] = domain.split(".")
            if len(domain_parts) == 4:
                return domain_parts[1]
        return None


def _is_valid_sqs_url(url: str) -> bool:
    """
    Checks if the URL is a valid SQS URL.
    """
    if url is None:
        return False
    split_url: List[str] = url.split("/")
    return (
        len(split_url) == 3
        and split_url[0].lower().startswith("sqs")
        and _is_account_id(split_url[1])
        and _is_valid_queue_name(split_url[2])
    )


def _is_account_id(input_str: str) -> bool:
    if input_str is None or len(input_str) != 12:
        return False

    try:
        int(input_str)
    except ValueError:
        return False

    return True


def _is_valid_queue_name(input_str: str) -> bool:
    if input_str is None or len(input_str) == 0 or len(input_str) > 80:
        return False

    for char in input_str:
        if char != "_" and char != "-" and not char.isalpha() and not char.isdigit():
            return False

    return True
