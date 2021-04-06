import os

import pytest
import httpx
from httpx import _client

from HttpxLibrary import HttpxLibrary
from HttpxLibrary.utils import is_file_descriptor, merge_headers, warn_if_equal_symbol_in_url
from utests import SCRIPT_DIR
from utests import mock


def test_none():
    assert is_file_descriptor(None) is False


def test_is_not_file_descriptor():
    nf = 'a string'
    assert is_file_descriptor(nf) is False


def test_is_file_descriptor():
    with open(os.path.join(SCRIPT_DIR, './test_utils.py')) as fd:
        assert is_file_descriptor(fd) is True


def test_merge_headers_with_session_headers_only():
    session = httpx.Client()
    merged = merge_headers(session, None)
    assert merged == session.headers


def test_merge_headers_with_all_none():
    session = httpx.Client()
    session.headers = None
    merged = merge_headers(session, None)
    assert merged == {}


def test_merge_headers_with_all():
    session = httpx.Client()
    headers = {'Content-Type': 'test'}
    merged = merge_headers(session, headers)
    session.headers.update(headers)
    assert merged == session.headers


@pytest.fixture(scope='function')
def mocked_keywords():
    keywords = HttpxLibrary()
    keywords._cache = mock.MagicMock()
    keywords._common_request = mock.MagicMock()
    keywords._check_status = mock.MagicMock()
    return keywords


@mock.patch('HttpxLibrary.utils.logger')
def test_no_warn_if_url_passed_as_named(mocked_logger, mocked_keywords):
    mocked_keywords.get_on_session('alias', url='http://this.is.an.url')
    mocked_logger.warn.assert_not_called()


@mock.patch('HttpxLibrary.utils.logger')
def test_no_warn_if_url_passed_as_positional(mocked_logger, mocked_keywords):
    mocked_keywords.get_on_session('alias', 'http://this.is.an.url')
    mocked_logger.warn.assert_not_called()


@mock.patch('HttpxLibrary.utils.logger')
def test_warn_that_url_is_missing(mocked_logger, mocked_keywords):
    try:
        mocked_keywords.get_on_session(alias=None)
    except TypeError:
        pass
    mocked_logger.warn.assert_called()
