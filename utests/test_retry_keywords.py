import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import httpx
from HttpxLibrary.RetryKeywords import RetryKeywords, RetryConfig


class TestRetryKeywords(unittest.TestCase):
    
    def setUp(self):
        self.retry_keywords = RetryKeywords()
    
    def test_retry_config_creation(self):
        """Test RetryConfig creation with default values"""
        config = RetryConfig()
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.backoff_factor, 0.3)
        self.assertEqual(config.backoff_max, 120.0)
        self.assertEqual(config.retry_on_status, [500, 502, 503, 504, 429])
        self.assertTrue(config.jitter)
    
    def test_retry_config_custom_values(self):
        """Test RetryConfig creation with custom values"""
        config = RetryConfig(
            max_retries=5,
            backoff_factor=0.5,
            retry_on_status=[500, 503],
            jitter=False
        )
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.backoff_factor, 0.5)
        self.assertEqual(config.retry_on_status, [500, 503])
        self.assertFalse(config.jitter)
    
    def test_should_retry_status(self):
        """Test status code retry logic"""
        config = RetryConfig(retry_on_status=[500, 502, 503])
        
        self.assertTrue(config.should_retry_status(500))
        self.assertTrue(config.should_retry_status(502))
        self.assertTrue(config.should_retry_status(503))
        self.assertFalse(config.should_retry_status(200))
        self.assertFalse(config.should_retry_status(404))
    
    def test_should_retry_exception(self):
        """Test exception retry logic"""
        config = RetryConfig()
        
        self.assertTrue(config.should_retry_exception(httpx.ConnectError("Connection failed")))
        self.assertTrue(config.should_retry_exception(httpx.TimeoutException("Timeout")))
        self.assertFalse(config.should_retry_exception(ValueError("Invalid value")))
    
    def test_backoff_time_calculation(self):
        """Test backoff time calculation"""
        config = RetryConfig(backoff_factor=1.0, jitter=False)
        
        # Test exponential backoff without jitter
        self.assertEqual(config.get_backoff_time(0), 1.0)  # 1.0 * (2^0) = 1.0
        self.assertEqual(config.get_backoff_time(1), 2.0)  # 1.0 * (2^1) = 2.0
        self.assertEqual(config.get_backoff_time(2), 4.0)  # 1.0 * (2^2) = 4.0
    
    def test_backoff_time_with_max(self):
        """Test backoff time respects maximum"""
        config = RetryConfig(backoff_factor=10.0, backoff_max=5.0, jitter=False)
        
        # Should be capped at backoff_max
        self.assertEqual(config.get_backoff_time(10), 5.0)
    
    def test_set_global_retry_configuration(self):
        """Test setting global retry configuration"""
        self.retry_keywords.set_global_retry_configuration(
            max_retries=5,
            backoff_factor=0.5,
            retry_on_status="500,502,503"
        )
        
        config = self.retry_keywords.global_retry_config
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.backoff_factor, 0.5)
        self.assertEqual(config.retry_on_status, [500, 502, 503])
    
    def test_set_session_retry_configuration(self):
        """Test setting session-specific retry configuration"""
        self.retry_keywords.set_session_retry_configuration(
            "test_session",
            max_retries=10,
            backoff_factor=1.0
        )
        
        config = self.retry_keywords.session_retry_configs["test_session"]
        self.assertEqual(config.max_retries, 10)
        self.assertEqual(config.backoff_factor, 1.0)
    
    def test_get_retry_configuration(self):
        """Test getting retry configuration"""
        # Test global configuration
        global_config = self.retry_keywords.get_retry_configuration()
        self.assertEqual(global_config['max_retries'], 3)  # default value
        
        # Test session configuration
        self.retry_keywords.set_session_retry_configuration("test_session", max_retries=7)
        session_config = self.retry_keywords.get_retry_configuration("test_session")
        self.assertEqual(session_config['max_retries'], 7)
    
    def test_clear_session_retry_configuration(self):
        """Test clearing session retry configuration"""
        # Set session config
        self.retry_keywords.set_session_retry_configuration("test_session", max_retries=5)
        self.assertIn("test_session", self.retry_keywords.session_retry_configs)
        
        # Clear session config
        self.retry_keywords.clear_session_retry_configuration("test_session")
        self.assertNotIn("test_session", self.retry_keywords.session_retry_configs)
    
    def test_get_retry_config_hierarchy(self):
        """Test retry configuration hierarchy (session > global)"""
        # Set global config
        self.retry_keywords.set_global_retry_configuration(max_retries=3)
        
        # Should return global config for non-existent session
        config = self.retry_keywords._get_retry_config("non_existent")
        self.assertEqual(config.max_retries, 3)
        
        # Set session config
        self.retry_keywords.set_session_retry_configuration("test_session", max_retries=7)
        
        # Should return session config
        config = self.retry_keywords._get_retry_config("test_session")
        self.assertEqual(config.max_retries, 7)
    
    @patch('time.sleep')
    def test_execute_with_retry_success_immediately(self, mock_sleep):
        """Test successful request on first attempt"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_request_func = Mock(return_value=mock_response)
        config = RetryConfig(max_retries=3)
        
        result = self.retry_keywords._execute_with_retry(mock_request_func, config)
        
        self.assertEqual(result, mock_response)
        mock_request_func.assert_called_once()
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_execute_with_retry_success_after_retries(self, mock_sleep):
        """Test successful request after retries"""
        # First call returns 500, second call returns 200
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        
        mock_request_func = Mock(side_effect=[mock_response_fail, mock_response_success])
        config = RetryConfig(max_retries=3, retry_on_status=[500])
        
        result = self.retry_keywords._execute_with_retry(mock_request_func, config)
        
        self.assertEqual(result, mock_response_success)
        self.assertEqual(mock_request_func.call_count, 2)
        mock_sleep.assert_called_once()
    
    @patch('time.sleep')
    def test_execute_with_retry_max_retries_exceeded(self, mock_sleep):
        """Test max retries exceeded"""
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_request_func = Mock(return_value=mock_response)
        config = RetryConfig(max_retries=2, retry_on_status=[500])
        
        result = self.retry_keywords._execute_with_retry(mock_request_func, config)
        
        # Should return the last failed response
        self.assertEqual(result, mock_response)
        self.assertEqual(mock_request_func.call_count, 3)  # initial + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('time.sleep')
    def test_execute_with_retry_exception_handling(self, mock_sleep):
        """Test retry on exceptions"""
        # First call raises exception, second call succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_request_func = Mock(side_effect=[httpx.ConnectError("Connection failed"), mock_response])
        config = RetryConfig(max_retries=3)
        
        result = self.retry_keywords._execute_with_retry(mock_request_func, config)
        
        self.assertEqual(result, mock_response)
        self.assertEqual(mock_request_func.call_count, 2)
        mock_sleep.assert_called_once()
    
    @patch('time.sleep')
    def test_execute_with_retry_non_retryable_exception(self, mock_sleep):
        """Test non-retryable exception is raised immediately"""
        mock_request_func = Mock(side_effect=ValueError("Invalid value"))
        config = RetryConfig(max_retries=3)
        
        with self.assertRaises(ValueError):
            self.retry_keywords._execute_with_retry(mock_request_func, config)
        
        mock_request_func.assert_called_once()
        mock_sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
