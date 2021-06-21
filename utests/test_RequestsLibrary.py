from HttpxLibrary import HttpxLibrary, HttpxOnSessionKeywords
from HttpxLibrary.HttpxKeywords import HttpxKeywords
from HttpxLibrary.SessionKeywords import SessionKeywords


class TestHttpxLibraryInheritance:

    @classmethod
    def setup_class(cls):
        cls.httpx_library = HttpxLibrary()

    def test_make_sure_is_instance_of_httpx_keywords(self):
        assert isinstance(self.httpx_library, HttpxKeywords)

    def test_make_sure_is_instance_of_session_keywords(self):
        assert isinstance(self.httpx_library, SessionKeywords)

    #    def test_make_sure_is_instance_of_deprecated_keywords(self):
    #        assert isinstance(self.httpx_library, DeprecatedKeywords)

    def test_make_sure_is_instance_of_httpx_on_session_keywords(self):
        assert isinstance(self.httpx_library, HttpxOnSessionKeywords)

    def test_make_sure_it_has_methods_from_httpx_keywords(self):
        assert hasattr(self.httpx_library, '_common_request')

    def test_make_sure_it_has_methods_from_session_keywords(self):
        assert hasattr(self.httpx_library, '_create_session')

    #    def test_make_sure_it_has_methods_from_deprecated_keywords(self):
    #        assert hasattr(self.httpx_library, 'get_request')

    def test_make_sure_it_has_methods_from_httpx_on_session_keywords(self):
        assert hasattr(self.httpx_library, 'get_on_session')
