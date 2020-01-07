from uuid import uuid4
import logging
import json
import requests

from django.conf import settings


log = logging.getLogger(__name__)


class TextExtractionError(Exception):
    pass


class TextExtractionTimeout(Exception):
    pass


def extract_text(file):
    headers = {
        'Accept': 'application/json',
        'Content-Disposition': f'attachment; filename={uuid4()}',
    }

    try:
        tika_response = requests.put(
            f'{settings.TIKA_URL}/rmeta/text',
            data=file,
            headers=headers,
            verify=False,
            timeout=settings.TIKA_TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise TextExtractionTimeout
    except Exception as ex:
        raise TextExtractionError(str(ex))

    try:
        tika_data = tika_response.json()
        content = tika_data[0]['X-TIKA:content'].strip()
    except (IndexError, AttributeError):  # Tika could not extract any text
        raise TextExtractionError
    except json.decoder.JSONDecodeError:  # Tika's response was not valid JSON
        return ''
    except KeyError:  # Tika could not detect any text content
        return ''

    return content
