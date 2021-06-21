import sys

from requests.compat import OrderedDict  # noqa
from requests.sessions import merge_cookies, merge_setting  # noqa
from requests.structures import CaseInsensitiveDict  # noqa

PY3 = sys.version_info > (3,)

if PY3:
    import http.client as httplib  # noqa
    from urllib.parse import urlencode  # noqa
else:
    import httplib  # noqa
    from urllib import urlencode  # noqa
