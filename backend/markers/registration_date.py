import dateutil.parser
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

from whoisapi import Client


def check_date_difference(date_str1, date_str2):
    date_formats = ['%Y.%m.%d %H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']

    def parse_date(date_str):
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        # Try parsing ISO 8601 format with dateutil.parser
        try:
            return dateutil.parser.isoparse(date_str)
        except ValueError:
            pass
        # If all parsing attempts fail, return warning
        return 'warning'

    # Parse both date strings
    date1 = parse_date(date_str1)
    date2 = parse_date(date_str2)

    # Ensure datetime objects are timezone-aware
    if date1.tzinfo is None:
        date1 = date1.replace(tzinfo=timezone.utc)
    if date2.tzinfo is None:
        date2 = date2.replace(tzinfo=timezone.utc)

    # Calculate the absolute difference between the two dates
    diff = abs(date2 - date1)

    days_difference = diff.total_seconds() / (24 * 3600)
    years_difference = days_difference / 365.25  # Average days per year

    if years_difference < 1:
        return False
    elif 1 <= years_difference < 2:
        return 'warning'
    else:
        return True


def registration_date(url):
    domain = urlparse(url).netloc
    client = Client(api_key='at_VQvXEBUtXlpmOCPwvIjgR8q56mA0G')
    result = json.loads(client.raw_data(domain))
    creation_date = result["WhoisRecord"]["registryData"]["createdDate"]
    expiration_date = result["WhoisRecord"]["registryData"]["expiresDate"]

    return check_date_difference(creation_date, expiration_date)
