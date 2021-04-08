import sys
import logging

import httpx
from .compat import merge_setting, merge_cookies
from httpx._models import Response
from httpx._config import DEFAULT_TIMEOUT_CONFIG, DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS

from robot.api import logger
from robot.api.deco import keyword
from robot.utils.asserts import assert_equal

from HttpxLibrary import utils, log
from HttpxLibrary.compat import httplib, PY3
from .HttpxKeywords import HttpxKeywords
from HttpxLibrary.exceptions import InvalidResponse, InvalidExpectedStatus
from HttpxLibrary.utils import is_file_descriptor, is_string_type

try:
    from httpx_ntlm import HttpNtlmAuth
except ImportError:
    pass


class SessionKeywords(HttpxKeywords):

    def _create_session(
            self,
            alias,
            url,
            auth,
            params,
            headers,
            cookies,
            verify,
            cert,
            http2,
            proxies,
            limits,
            pool_limits,
            max_redirects,
            base_url,
            debug,
            max_retries,
            disable_warnings,
            timeout):

        logger.debug('Creating session: %s' % alias)

        try:
            max_retries = int(max_retries)
        except ValueError as err:
            raise ValueError("Error converting session parameter: %s" % err)

        transport = httpx.HTTPTransport(retries=max_retries)
        s = session = httpx.Client(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http2=http2,
            proxies=proxies,
            timeout=timeout,
            limits=limits,
            pool_limits=pool_limits,
            max_redirects=max_redirects,
            base_url=base_url,
            transport=transport)

        # Disable requests warnings, useful when you have large number of testcase
        # you will observe drastical changes in Robot log.html and output.xml files size
        if disable_warnings:
            # you need to initialize logging, otherwise you will not see anything from requests
            logging.basicConfig()
            logging.getLogger().setLevel(logging.ERROR)
            httpx_log = logging.getLogger("httpx")
            httpx_log.setLevel(logging.ERROR)
            httpx_log.propagate = True
            if not verify:
                httpx.packages.urllib3.disable_warnings()

        # verify can be a Boolean or a String
        if isinstance(verify, bool):
            s.verify = verify
        elif utils.is_string_type(verify):
            if verify.lower() == 'true' or verify.lower() == 'false':
                s.verify = self.builtin.convert_to_boolean(verify)
            else:
                # String for CA_BUNDLE, not a Boolean String
                s.verify = verify
        else:
            # not a Boolean nor a String
            s.verify = verify

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
            auth=None,
            params=None,
            headers={},
            cookies={},
            verify=False,
            cert=None,
            http2=True,
            proxies=None,
            limits=DEFAULT_LIMITS,
            pool_limits=None,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            base_url="",
            debug=0,
            max_retries=3,
            disable_warnings=0,
            timeout=None):
        """ Create Session: create a HTTP session to a server

        ``alias`` Robot Framework alias to identify the session

        ``url`` Base url of the server

        ``auth`` List of username & password for HTTP Basic Auth

        ``params`` Dictionary of query parameters (param of HTTPX.Client)

        ``headers`` Dictionary of default headers

        ``cookies`` Dictionary of cookies

        ``verify`` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.

        ``cert`` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.

        ``http2`` Boolean, True = HTTP/2, False = HTTP/1.1

        ``timeout`` Connection timeout

        ``proxies`` Dictionary that contains proxy urls for HTTP and HTTPS communication


        ``debug`` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable httpx warning useful when you have large number of testcases

        ``backoff_factor`` Introduces a delay time between retries that is longer after each retry.
                           eg. if backoff_factor is set to 0.1
                           the sleep between attemps will be: 0.0, 0.2, 0.4
                           More info here: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html

        ``retry_method_list`` List of uppercased HTTP method verbs where retries are allowed.
                              By default retries are allowed only on HTTP requests methods that are considered to be
                              idempotent (multiple requests with the same parameters end with the same state).
                              eg. set to ['POST', 'GET'] to retry only those kind of requests.

        ``retry_status_list`` List of integer HTTP status codes that, if returned, a retry is attempted.
                              eg. set to [502, 503] to retry requests if those status are returned.
                              Note that max_retries must be greater than 0.

        """
        basic_auth = httpx.auth.BasicAuth(*auth) if auth else None

        logger.info('Creating Session using : alias=%s, url=%s, headers=%s, \
                    cookies=%s, auth=%s, timeout=%s,  verify=%s, \
                    debug=%s ' % (alias, url, headers, cookies, auth, timeout,
                                  verify, debug))
        return self._create_session(
            alias=alias,
            url=url,
            auth=basic_auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http2=http2,
            proxies=proxies,
            limits=limits,
            pool_limits=pool_limits,
            max_redirects=max_redirects,
            base_url=base_url,
            debug=debug,
            max_retries=max_retries,
            disable_warnings=disable_warnings,
            timeout=timeout)

    @keyword("Create Custom Session")
    def create_custom_session(
            self,
            alias,
            url,
            auth=None,
            params=None,
            headers={},
            cookies={},
            verify=False,
            cert=None,
            http2=True,
            proxies=None,
            limits=DEFAULT_LIMITS,
            pool_limits=None,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            base_url="",
            debug=0,
            max_retries=3,
            disable_warnings=0,
            timeout=None):
        """ Create Session: create a HTTP session to a server

        ``url`` Base url of the server

        ``alias`` Robot Framework alias to identify the session

        ``headers`` Dictionary of default headers

        ``cookies`` Dictionary of cookies

        ``auth`` A Custom Authentication object to be passed on to the requests library.
                http://docs.python-requests.org/en/master/user/advanced/#custom-authentication

        ``timeout`` Connection timeout

        ``proxies`` Dictionary that contains proxy urls for HTTP and HTTPS communication

        ``verify`` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        ``debug`` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable requests warning useful when you have large number of testcases

        ``backoff_factor`` Introduces a delay time between retries that is longer after each retry.
                           eg. if backoff_factor is set to 0.1
                           the sleep between attemps will be: 0.0, 0.2, 0.4
                           More info here: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html

        ``retry_method_list`` List of uppercased HTTP method verbs where retries are allowed.
                              By default retries are allowed only on HTTP requests methods that are considered to be
                              idempotent (multiple requests with the same parameters end with the same state).
                              eg. set to ['POST', 'GET'] to retry only those kind of requests.

        ``retry_status_list`` List of integer HTTP status codes that, if returned, a retry is attempted.
                              eg. set to [502, 503] to retry requests if those status are returned.
                              Note that max_retries must be greater than 0.
        """

        logger.info('Creating Custom Authenticated Session using : alias=%s, url=%s, headers=%s, \
                    cookies=%s, auth=%s, timeout=%s, verify=%s, \
                    debug=%s ' % (alias, url, headers, cookies, auth, timeout,
                                  verify, debug))

        return self._create_session(
            alias=alias,
            url=url,
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http2=http2,
            proxies=proxies,
            limits=limits,
            pool_limits=pool_limits,
            max_redirects=max_redirects,
            base_url=base_url,
            debug=debug,
            max_retries=max_retries,
            disable_warnings=disable_warnings,
            timeout=timeout)

    @keyword("Create Digest Session")
    def create_digest_session(
            self,
            alias,
            url,
            auth=None,
            params=None,
            headers={},
            cookies={},
            verify=False,
            cert=None,
            http2=True,
            proxies=None,
            limits=DEFAULT_LIMITS,
            pool_limits=None,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            base_url="",
            debug=0,
            max_retries=3,
            disable_warnings=0,
            timeout=None):
        """ Create Session: create a HTTP session to a server

        ``url`` Base url of the server

        ``alias`` Robot Framework alias to identify the session

        ``headers`` Dictionary of default headers

        ``cookies`` Dictionary of cookies

        ``auth`` ['DOMAIN', 'username', 'password'] for NTLM Authentication

        ``timeout`` Connection timeout

        ``proxies`` Dictionary that contains proxy urls for HTTP and HTTPS communication

        ``verify`` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        ``debug`` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable requests warning useful when you have large number of testcases

        ``backoff_factor`` Introduces a delay time between retries that is longer after each retry.
                           eg. if backoff_factor is set to 0.1
                           the sleep between attemps will be: 0.0, 0.2, 0.4
                           More info here: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html

        ``retry_method_list`` List of uppercased HTTP method verbs where retries are allowed.
                              By default retries are allowed only on HTTP requests methods that are considered to be
                              idempotent (multiple requests with the same parameters end with the same state).
                              eg. set to ['POST', 'GET'] to retry only those kind of requests.

        ``retry_status_list`` List of integer HTTP status codes that, if returned, a retry is attempted.
                              eg. set to [502, 503] to retry requests if those status are returned.
                              Note that max_retries must be greater than 0.
        """
        digest_auth = httpx.auth.DigestAuth(*auth) if auth else None

        return self._create_session(
            alias=alias,
            url=url,
            auth=digest_auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http2=http2,
            proxies=proxies,
            limits=limits,
            pool_limits=pool_limits,
            max_redirects=max_redirects,
            base_url=base_url,
            debug=debug,
            max_retries=max_retries,
            disable_warnings=disable_warnings,
            timeout=timeout)

    @keyword("Create Ntlm Session")
    def create_ntlm_session(
            self,
            alias,
            url,
            auth=None,
            params=None,
            headers={},
            cookies={},
            verify=False,
            cert=None,
            http2=True,
            proxies=None,
            limits=DEFAULT_LIMITS,
            pool_limits=None,
            max_redirects=DEFAULT_MAX_REDIRECTS,
            base_url="",
            debug=0,
            max_retries=3,
            disable_warnings=0,
            timeout=None):
        """ Create Session: create a HTTP session to a server

        ``url`` Base url of the server

        ``alias`` Robot Framework alias to identify the session

        ``headers`` Dictionary of default headers

        ``cookies`` Dictionary of cookies

        ``auth`` ['DOMAIN', 'username', 'password'] for NTLM Authentication

        ``timeout`` Connection timeout

        ``proxies`` Dictionary that contains proxy urls for HTTP and HTTPS communication

        ``verify`` Whether the SSL cert will be verified. A CA_BUNDLE path can also be provided.
                 Defaults to False.

        ``debug`` Enable http verbosity option more information
                https://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.set_debuglevel

        ``max_retries`` Number of maximum retries each connection should attempt.
                        By default it will retry 3 times in case of connection errors only.
                        A 0 value will disable any kind of retries regardless of other retry settings.
                        In case the number of retries is reached a retry exception is raised.

        ``disable_warnings`` Disable requests warning useful when you have large number of testcases

        ``backoff_factor`` Introduces a delay time between retries that is longer after each retry.
                           eg. if backoff_factor is set to 0.1
                           the sleep between attemps will be: 0.0, 0.2, 0.4
                           More info here: https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html

        ``retry_method_list`` List of uppercased HTTP method verbs where retries are allowed.
                              By default retries are allowed only on HTTP requests methods that are considered to be
                              idempotent (multiple requests with the same parameters end with the same state).
                              eg. set to ['POST', 'GET'] to retry only those kind of requests.

        ``retry_status_list`` List of integer HTTP status codes that, if returned, a retry is attempted.
                              eg. set to [502, 503] to retry requests if those status are returned.
                              Note that max_retries must be greater than 0.
        """
        try:
            HttpNtlmAuth
        except NameError:
            raise AssertionError('httpx-ntlm module not installed')
        if len(auth) != 3:
            raise AssertionError('Incorrect number of authentication arguments'
                                 ' - expected 3, got {}'.format(len(auth)))
        else:
            ntlm_auth = HttpNtlmAuth('{}\\{}'.format(auth[0], auth[1]),
                                     auth[2])
            logger.info('Creating NTLM Session using : alias=%s, url=%s, \
                        headers=%s, cookies=%s, ntlm_auth=%s, timeout=%s, \
                        verify=%s, debug=%s '
                        % (alias, url, headers, cookies, ntlm_auth,
                           timeout, verify, debug))

            return self._create_session(
                alias=alias,
                url=url,
                auth=ntlm_auth,
                params=params,
                headers=headers,
                cookies=cookies,
                verify=verify,
                cert=cert,
                http2=http2,
                proxies=proxies,
                limits=limits,
                pool_limits=pool_limits,
                max_redirects=max_redirects,
                base_url=base_url,
                debug=debug,
                max_retries=max_retries,
                disable_warnings=disable_warnings,
                timeout=timeout)

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
        # print("My info", session, method)
        # print(f" Kwargs: {kwargs}" )
        self._capture_output()

        #if method = get atch the api in _api from httpx
        resp = method_function(
            self._get_url(session, uri),
            **kwargs)

        log.log_request(resp)
        self._print_debug()
        session.last_resp = resp
        log.log_response(resp)

        #data = kwargs.get('data', None)
        #epkcfsm remove this is request was a get
        #if method is "get"
        #   if is_file_descriptor(data):
        #      data.close()

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
