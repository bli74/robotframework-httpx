import logging
import sys

import httpx
from httpx import Client, HTTPTransport, Response
# noinspection PyProtectedMember
from httpx._config import DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT_CONFIG
from robot.api import logger
from robot.api.deco import keyword
from robot.utils.asserts import assert_equal

from HttpxLibrary import utils, log
from HttpxLibrary.compat import httplib
from HttpxLibrary.exceptions import InvalidResponse, InvalidExpectedStatus
from HttpxLibrary.utils import is_file_descriptor, is_string_type
from .HttpxKeywords import HttpxKeywords

try:
    # noinspection PyUnresolvedReferences
    from httpx_ntlm import HttpNtlmAuth
except ImportError:
    pass


class SessionKeywords(HttpxKeywords):
    DEFAULT_RETRIES = 3

    def _create_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            http1=True,
            http2=False,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False
    ) -> httpx.Client:

        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}
        logger.info('Create Session parameters:'
                    f'- alias={alias}'
                    f'- url={url}'
                    f'- auth={auth}'
                    f'- cert={cert}'
                    f'- cookies={cookies}'
                    f'- headers={headers}'
                    f'- http1={http1}'
                    f'- http2={http2}'
                    f'- limits={limits}'
                    f'- max_redirects={max_redirects}'
                    f'- params={params}'
                    f'- retries={retries}'
                    f'- timeout={timeout}'
                    f'- verify={verify}'

                    )

        transport = None
        # Retries parameter not supported directly by Client()
        if retries is not None and retries > 0:
            transport = HTTPTransport(
                verify=verify,
                cert=cert,
                http1=http1,
                http2=http2,
                limits=limits,
                retries=retries
            )

        s = session = Client(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            transport=transport
        )

        # Disable requests warnings, useful when you have large number of testcase
        # you will observe drastical changes in Robot log.html and output.xml files size
        if disable_warnings:
            # you need to initialize logging, otherwise you will not see anything from requests
            logging.basicConfig()
            logging.getLogger().setLevel(logging.ERROR)
            httpx_log = logging.getLogger("httpx")
            httpx_log.setLevel(logging.ERROR)
            httpx_log.propagate = True

        s.url = url

        # Enable http verbosity
        if int(debug) >= 1:
            self.debug = int(debug)
            httplib.HTTPConnection.debuglevel = self.debug

        self._cache.register(session, alias=alias)
        return session

    @keyword("Create Session")
    def create_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            http1=True,
            http2=False,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False
    ):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` Username and password pair or None for Basic Authentication
                 to use when sending requests.
                 See httpx.BasicAuth()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``http1`` Switch to enable/disable HTTP/1.1 support
                  See httpx.Client()

        ``http2`` Switch to enable/disable HTTP/2 support
                  See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = {}
        if auth is not None:
            auth = httpx.BasicAuth(*auth)

        logger.info('Create Session with Basic Authentication')

        return self._create_session(
            alias,
            url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            debug=debug,
            disable_warnings=disable_warnings,
            retries=retries
        )

    @keyword("Create HTTP2 Session")
    def create_http2_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False):
        """ Create Session: create a HTTP/2 only session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` Username and password pair or None for Basic Authentication
                 to use when sending requests.
                 See httpx.BasicAuth()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()
        """
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if auth is not None:
            auth = httpx.BasicAuth(*auth)

        logger.info('Create Session with Basic Authentication')

        return self._create_session(
            alias,
            url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=False,
            http2=True,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            debug=debug,
            disable_warnings=disable_warnings,
            retries=retries
        )

    @keyword("Create Custom Session")
    def create_custom_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            http1=True,
            http2=False,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` A Custom Authentication object to be passed on to the requests library.
                http://docs.python-requests.org/en/master/user/advanced/#custom-authentication

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``http1`` Switch to enable/disable HTTP/1.1 support
                  See httpx.Client()

        ``http2`` Switch to enable/disable HTTP/2 support
                  See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()
        """
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        logger.info('Creating Custom Authenticated Session')
        return self._create_session(
            alias=alias,
            url=url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            debug=debug,
            disable_warnings=disable_warnings,
            retries=retries)

    @keyword("Create Digest Session")
    def create_digest_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            http1=True,
            http2=False,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` Username and password pair or None for Digest Authentication
                 to use when sending requests.
                 See httpx.DigestAuth()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``http1`` Switch to enable/disable HTTP/1.1 support
                  See httpx.Client()

        ``http2`` Switch to enable/disable HTTP/2 support
                  See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()
        """
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if auth is not None:
            auth = httpx.DigestAuth(*auth)

        logger.info('Creating Session with Digest Authentication')

        return self._create_session(
            alias=alias,
            url=url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            debug=debug,
            disable_warnings=disable_warnings,
            retries=retries)

    @keyword("Create Ntlm Session")
    def create_ntlm_session(
            self,
            alias,
            url,
            *,
            # optional named args
            auth=None,
            cert=None,
            cookies=None,
            debug=0,
            disable_warnings=0,
            headers=None,
            http1=True,
            http2=False,
            limits=DEFAULT_LIMITS,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            params=None,
            retries=DEFAULT_RETRIES,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            verify=False):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` ['DOMAIN', 'username', 'password'] for NTLM Authentication.
                 See httpx_ntlm.HttpNtlmAuth()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``http1`` Switch to enable/disable HTTP/1.1 support
                  See httpx.Client()

        ``http2`` Switch to enable/disable HTTP/2 support
                  See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()
        """
        if cookies is None:
            cookies = {}
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        try:
            HttpNtlmAuth
        except NameError:
            raise AssertionError('httpx-ntlm module not installed')
        if len(auth) != 3:
            raise AssertionError('Incorrect number of authentication arguments'
                                 ' - expected 3, got {}'.format(len(auth)))
        else:
            auth = HttpNtlmAuth('{}\\{}'.format(auth[0], auth[1]),
                                auth[2])
            logger.info('Creating NTLM Session')

        return self._create_session(
            alias=alias,
            url=url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            timeout=timeout,
            limits=limits,
            max_redirects=max_redirects,
            debug=debug,
            disable_warnings=disable_warnings,
            retries=retries)

    @keyword("Session Exists")
    def session_exists(self, alias):
        """Return True if the session has been already created

        ``alias`` that has been used to identify the Session object in the cache
        """
        try:
            self._cache[alias]
            return True
        except RuntimeError:
            return False

    @keyword("Delete All Sessions")
    def delete_all_sessions(self):
        """ Removes all the session objects """
        logger.info('Delete All Sessions')

        self._cache.empty_cache()

    # TODO this is not covered by any tests
    @keyword("Update Session")
    def update_session(self, alias, headers=None, cookies=None):
        """Update Session Headers: update a HTTP Session Headers

        ``alias`` Robot Framework alias to identify the session

        ``headers`` Dictionary of headers merge into session
        """
        session = self._cache.switch(alias)
        if headers is not None:
            session.headers.update(headers)
        if cookies is not None:
            session.cookies.update(cookies)

    def _common_request(
            self,
            method,
            session,
            uri,
            **kwargs):

        method_function = getattr(session, method)
        self._capture_output()

        # if method = get atch the api in _api from httpx
        resp = method_function(
            self._get_url(session, uri),
            **kwargs)

        log.log_request(resp)
        self._print_debug()
        session.last_resp = resp
        log.log_response(resp)

        data = kwargs.get('data', None)
        # epkcfsm remove this if request was a get
        if method == "get":
            if is_file_descriptor(data):
                data.close()

        return resp

    @staticmethod
    def _check_status(expected_status, resp, msg=None):
        """
        Helper method to check HTTP status
        """
        if not isinstance(resp, Response):
            raise InvalidResponse(resp)
        if expected_status is None:
            resp.raise_for_status()
        else:
            if not is_string_type(expected_status):
                raise InvalidExpectedStatus(expected_status)
            if expected_status.lower() in ['any', 'anything']:
                return
            try:
                expected_status = int(expected_status)
            except ValueError:
                expected_status = utils.parse_named_status(expected_status)
            msg = '' if msg is None else '{} '.format(msg)
            msg = "{}Url: {} Expected status".format(msg, resp.url)
            assert_equal(resp.status_code, expected_status, msg)

    @staticmethod
    def _get_url(session, uri):
        """
        Helper method to get the full url
        """
        url = session.url
        if uri:
            slash = '' if uri.startswith('/') else '/'
            url = "%s%s%s" % (session.url, slash, uri)
        return url

    # FIXME might be broken we need a test for this
    @staticmethod
    def _get_timeout(timeout):
        return float(timeout) if timeout is not None else DEFAULT_TIMEOUT_CONFIG

    def _capture_output(self):
        if self.debug >= 1:
            self.http_log = utils.WritableObject()
            sys.stdout = self.http_log

    def _print_debug(self):
        if self.debug >= 1:
            sys.stdout = sys.__stdout__  # Restore stdout
            debug_info = ''.join(
                self.http_log.content).replace(
                '\\r',
                '').replace(
                '\'',
                '')

            # Remove empty lines
            debug_info = "\n".join(
                [ll.rstrip() for ll in debug_info.splitlines() if ll.strip()])
            logger.debug(debug_info)
