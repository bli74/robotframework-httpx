import logging
import sys

import httpx
from HttpxLibrary import utils, log
from HttpxLibrary.compat import httplib, PY3
from HttpxLibrary.exceptions import InvalidResponse, InvalidExpectedStatus
from HttpxLibrary.utils import is_file_descriptor, is_string_type
from httpx import Response
from robot.api import logger
from robot.api.deco import keyword
from robot.utils.asserts import assert_equal

from .HttpxKeywords import HttpxKeywords
from .compat import merge_setting, merge_cookies

try:
    from httpx_ntlm import HttpNtlmAuth
except ImportError:
    pass


class SessionKeywords(HttpxKeywords):

    def _create_session(
            self,
            alias: str,
            url: str,
            **kwargs: dict
    ) -> httpx.Client:

        logger.debug('Creating session: %s' % alias)

        # Get and remove arguments used locally from **kwargs
        debug = kwargs.pop('debug', False)
        max_retries = kwargs.pop('max_retries', 3)
        disable_warnings = kwargs.pop('disable_warnings', False)
        timeout = kwargs.pop('timeout', None)

        # Normalize max_retries
        try:
            max_retries = int(max_retries)
        except ValueError as err:
            raise ValueError("Error converting session parameter: %s" % err)

        kwargs['transport'] = httpx.HTTPTransport(retries=max_retries)
        s = session = httpx.Client(**kwargs)

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
            **kwargs):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` Username and password pair or None for Basic Authentication
                 to use when sending requests.
                 See httpx.BasicAuth()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``proxies`` A dictionary mapping proxy keys to proxy URLs.
                    See httpx.Client()

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``http2`` Switch to toggle between HTTP/1 (False) and HTTP/2 (True)
                  See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        """
        auth = kwargs.pop('auth', None)
        if auth is not None:
            kwargs['auth'] = httpx.BasicAuth(*auth)

        logger.info('Creating Session with Basic Authentication using : alias=%s, url=%s, kwargs=%s' \
                    % (alias, url, kwargs))

        return self._create_session(
            alias=alias,
            url=url,
            **kwargs)

    @keyword("Create Custom Session")
    def create_custom_session(
            self,
            alias,
            url,
            **kwargs):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` A Custom Authentication object to be passed on to the requests library.
                http://docs.python-requests.org/en/master/user/advanced/#custom-authentication

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``proxies`` A dictionary mapping proxy keys to proxy URLs.
                    See httpx.Client()

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``http2`` Switch to toggle between HTTP/1 (False) and HTTP/2 (True)
                  See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        """

        logger.info('Creating Custom Authenticated Session using : alias=%s, url=%s, kwargs=%s' \
                    % (alias, url, kwargs))

        return self._create_session(
            alias=alias,
            url=url,
            **kwargs)

    @keyword("Create Digest Session")
    def create_digest_session(
            self,
            alias,
            url,
            **kwargs):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` Username and password pair or None for Digest Authentication
                 to use when sending requests.
                 See httpx.DigestAuth()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``proxies`` A dictionary mapping proxy keys to proxy URLs.
                    See httpx.Client()

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``http2`` Switch to toggle between HTTP/1 (False) and HTTP/2 (True)
                  See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        """
        auth = kwargs.pop('auth', None)
        if auth is not None:
            kwargs['auth'] = httpx.DigestAuth(*auth)

        logger.info('Creating Session with Digest Authentication using : alias=%s, url=%s, kwargs=%s' \
                    % (alias, url, kwargs))

        return self._create_session(
            alias=alias,
            url=url,
            **kwargs)

    @keyword("Create Ntlm Session")
    def create_ntlm_session(
            self,
            alias,
            url,
            **kwargs):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` ['DOMAIN', 'username', 'password'] for NTLM Authentication.
                 See httpx_ntlm.HttpNtlmAuth()

        ``params`` Query parameters to include in request URLs, as
                   a string, dictionary, or sequence of two-tuples.
                   See httpx.Client()

        ``headers`` Dictionary of HTTP headers to include when sending requests.
                    See httpx.Client()

        ``cookies`` Dictionary of Cookie items to include when sending requests.
                    See httpx.Client()

        ``verify`` SSL certificates (a.k.a CA bundle) used to verify the identity
                   of requested hosts. Either `True` (default CA bundle),
                   a path to an SSL certificate file, or `False` (disable verification).
                   See httpx.Client()

        ``cert`` An SSL certificate used by the requested host to authenticate the client.
                 Either a path to an SSL certificate file, or two-tuple of (certificate file,
                 key file), or a three-tuple of (certificate file, key file, password).
                 See httpx.Client()

        ``proxies`` A dictionary mapping proxy keys to proxy URLs.
                    See httpx.Client()

        ``timeout`` The timeout configuration to use when sending requests.
                    See httpx.Client()

        ``limits`` The limits configuration to use.
                   See httpx.Client()

        ``max_redirects`` The maximum number of redirect responses that should be followed.
                          See httpx.Client()

        ``http2`` Switch to toggle between HTTP/1 (False) and HTTP/2 (True)
                  See httpx.Client()

        ``debug`` Enable http verbosity option more information
                  https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        """
        try:
            HttpNtlmAuth
        except NameError:
            raise AssertionError('httpx-ntlm module not installed')
        auth = kwargs.pop('auth', None)
        if len(auth) != 3:
            raise AssertionError('Incorrect number of authentication arguments'
                                 ' - expected 3, got {}'.format(len(auth)))
        else:
            kwargs['auth'] = HttpNtlmAuth('{}\\{}'.format(auth[0], auth[1]),
                                          auth[2])
            logger.info('Creating NTLM Session using : alias=%s, url=%s, kwargs=%s '
                        % (alias, url, kwargs))

        return self._create_session(
            alias=alias,
            url=url,
            **kwargs)

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
        session.headers = merge_setting(headers, session.headers)
        session.cookies = merge_cookies(session.cookies, cookies)

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
        if method is "get":
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
    def _get_timeout(self, timeout):
        return float(timeout) if timeout is not None else self.timeout

    def _capture_output(self):
        if self.debug >= 1:
            self.http_log = utils.WritableObject()
            sys.stdout = self.http_log

    def _print_debug(self):
        if self.debug >= 1:
            sys.stdout = sys.__stdout__  # Restore stdout
            if PY3:
                debug_info = ''.join(
                    self.http_log.content).replace(
                    '\\r',
                    '').replace(
                    '\'',
                    '')
            else:
                debug_info = ''.join(
                    self.http_log.content).replace(
                    '\\r',
                    '').decode('string_escape').replace(
                    '\'',
                    '')

            # Remove empty lines
            debug_info = "\n".join(
                [ll.rstrip() for ll in debug_info.splitlines() if ll.strip()])
            logger.debug(debug_info)
