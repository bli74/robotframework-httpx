import time
import random
from typing import List, Union, Callable, Optional
from robot.api import logger
from robot.api.deco import keyword
import httpx
from httpx import Response, HTTPStatusError, ConnectError, TimeoutException, RequestError


class RetryConfig:
    """Configuration class for retry behavior"""
    
    def __init__(self, 
                 max_retries: int = 3,
                 backoff_factor: float = 0.3,
                 backoff_max: float = 120.0,
                 retry_on_status: List[int] = None,
                 retry_on_exceptions: List[Exception] = None,
                 jitter: bool = True):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.backoff_max = backoff_max
        self.retry_on_status = retry_on_status or [500, 502, 503, 504, 429]
        self.retry_on_exceptions = retry_on_exceptions or [
            ConnectError, TimeoutException, RequestError
        ]
        self.jitter = jitter
    
    def should_retry_status(self, status_code: int) -> bool:
        """Check if we should retry based on status code"""
        return status_code in self.retry_on_status
    
    def should_retry_exception(self, exception: Exception) -> bool:
        """Check if we should retry based on exception type"""
        return any(isinstance(exception, exc_type) for exc_type in self.retry_on_exceptions)
    
    def get_backoff_time(self, attempt: int) -> float:
        """Calculate backoff time for given attempt"""
        backoff = self.backoff_factor * (2 ** attempt)
        if self.jitter:
            backoff *= (0.5 + random.random() * 0.5)  # Add jitter
        return min(backoff, self.backoff_max)


class RetryKeywords:
    """Keywords for enhanced retry mechanisms"""
    
    def __init__(self):
        self.global_retry_config = RetryConfig()
        self.session_retry_configs = {}
    
    @keyword("Set Global Retry Configuration")
    def set_global_retry_configuration(self, 
                                     max_retries: int = 3,
                                     backoff_factor: float = 0.3,
                                     backoff_max: float = 120.0,
                                     retry_on_status: Union[str, List[int]] = "500,502,503,504,429",
                                     jitter: bool = True):
        """
        Sets global retry configuration for all HTTP requests.
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_factor: Backoff factor for exponential backoff (default: 0.3)
            backoff_max: Maximum backoff time in seconds (default: 120.0)
            retry_on_status: HTTP status codes to retry on, comma-separated string or list (default: "500,502,503,504,429")
            jitter: Whether to add random jitter to backoff times (default: True)
        
        Examples:
        | Set Global Retry Configuration | max_retries=5 | backoff_factor=0.5 |
        | Set Global Retry Configuration | retry_on_status=500,502,503 | jitter=False |
        """
        # Convert parameters to correct types (Robot Framework passes everything as strings)
        max_retries = int(max_retries)
        backoff_factor = float(backoff_factor)
        backoff_max = float(backoff_max)
        jitter = bool(jitter) if isinstance(jitter, bool) else str(jitter).lower() in ('true', '1', 'yes')
        
        if isinstance(retry_on_status, str):
            retry_on_status = [int(code.strip()) for code in retry_on_status.split(',')]
        
        self.global_retry_config = RetryConfig(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            backoff_max=backoff_max,
            retry_on_status=retry_on_status,
            jitter=jitter
        )
        
        logger.info(f"Global retry configuration set: max_retries={max_retries}, "
                   f"backoff_factor={backoff_factor}, retry_on_status={retry_on_status}")
    
    @keyword("Set Session Retry Configuration")
    def set_session_retry_configuration(self, 
                                      alias: str,
                                      max_retries: int = 3,
                                      backoff_factor: float = 0.3,
                                      backoff_max: float = 120.0,
                                      retry_on_status: Union[str, List[int]] = "500,502,503,504,429",
                                      jitter: bool = True):
        """
        Sets retry configuration for a specific session.
        
        Args:
            alias: Session alias name
            max_retries: Maximum number of retry attempts (default: 3)
            backoff_factor: Backoff factor for exponential backoff (default: 0.3)
            backoff_max: Maximum backoff time in seconds (default: 120.0)
            retry_on_status: HTTP status codes to retry on, comma-separated string or list (default: "500,502,503,504,429")
            jitter: Whether to add random jitter to backoff times (default: True)
        
        Examples:
        | Set Session Retry Configuration | my_session | max_retries=5 |
        | Set Session Retry Configuration | api_session | retry_on_status=429,503 | backoff_factor=1.0 |
        """
        # Convert parameters to correct types (Robot Framework passes everything as strings)
        max_retries = int(max_retries)
        backoff_factor = float(backoff_factor)
        backoff_max = float(backoff_max)
        jitter = bool(jitter) if isinstance(jitter, bool) else str(jitter).lower() in ('true', '1', 'yes')
        
        if isinstance(retry_on_status, str):
            retry_on_status = [int(code.strip()) for code in retry_on_status.split(',')]
        
        self.session_retry_configs[alias] = RetryConfig(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            backoff_max=backoff_max,
            retry_on_status=retry_on_status,
            jitter=jitter
        )
        
        logger.info(f"Session '{alias}' retry configuration set: max_retries={max_retries}, "
                   f"backoff_factor={backoff_factor}, retry_on_status={retry_on_status}")
    
    @keyword("Get Retry Configuration")
    def get_retry_configuration(self, alias: Optional[str] = None) -> dict:
        """
        Gets the current retry configuration for a session or global configuration.
        
        Args:
            alias: Session alias name. If None, returns global configuration.
        
        Returns:
            Dictionary containing retry configuration
        
        Examples:
        | ${config}= | Get Retry Configuration |
        | ${config}= | Get Retry Configuration | my_session |
        """
        if alias and alias in self.session_retry_configs:
            config = self.session_retry_configs[alias]
        else:
            config = self.global_retry_config
        
        return {
            'max_retries': config.max_retries,
            'backoff_factor': config.backoff_factor,
            'backoff_max': config.backoff_max,
            'retry_on_status': config.retry_on_status,
            'jitter': config.jitter
        }
    
    @keyword("Clear Session Retry Configuration")
    def clear_session_retry_configuration(self, alias: str):
        """
        Clears retry configuration for a specific session, falling back to global configuration.
        
        Args:
            alias: Session alias name
        
        Examples:
        | Clear Session Retry Configuration | my_session |
        """
        if alias in self.session_retry_configs:
            del self.session_retry_configs[alias]
            logger.info(f"Retry configuration cleared for session '{alias}'")
        else:
            logger.warn(f"No retry configuration found for session '{alias}'")
    
    def _get_retry_config(self, alias: Optional[str] = None) -> RetryConfig:
        """Get retry configuration for session or global"""
        if alias and alias in self.session_retry_configs:
            return self.session_retry_configs[alias]
        return self.global_retry_config
    
    def _execute_with_retry(self, 
                           request_func: Callable,
                           retry_config: RetryConfig,
                           *args, **kwargs) -> Response:
        """
        Execute HTTP request with retry logic
        
        Args:
            request_func: Function to execute (e.g., session.get)
            retry_config: Retry configuration to use
            *args, **kwargs: Arguments to pass to request_func
        
        Returns:
            HTTP Response object
        """
        last_exception = None
        last_response = None
        
        for attempt in range(retry_config.max_retries + 1):
            try:
                response = request_func(*args, **kwargs)
                
                # Check if we should retry based on status code
                if retry_config.should_retry_status(response.status_code):
                    last_response = response
                    if attempt < retry_config.max_retries:
                        backoff_time = retry_config.get_backoff_time(attempt)
                        logger.warn(f"Request failed with status {response.status_code}, "
                                   f"retrying in {backoff_time:.2f} seconds (attempt {attempt + 1}/{retry_config.max_retries + 1})")
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.warn(f"Request failed with status {response.status_code}, "
                                   f"max retries ({retry_config.max_retries}) exceeded")
                        return response
                
                # Success case
                if attempt > 0:
                    logger.info(f"Request succeeded on attempt {attempt + 1}")
                return response
                
            except Exception as e:
                last_exception = e
                
                # Check if we should retry based on exception type
                if retry_config.should_retry_exception(e):
                    if attempt < retry_config.max_retries:
                        backoff_time = retry_config.get_backoff_time(attempt)
                        logger.warn(f"Request failed with {type(e).__name__}: {str(e)}, "
                                   f"retrying in {backoff_time:.2f} seconds (attempt {attempt + 1}/{retry_config.max_retries + 1})")
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.warn(f"Request failed with {type(e).__name__}: {str(e)}, "
                                   f"max retries ({retry_config.max_retries}) exceeded")
                        raise e
                else:
                    # Don't retry for this exception type
                    raise e
        
        # This should not be reached, but just in case
        if last_exception:
            raise last_exception
        if last_response:
            return last_response
        
        raise RuntimeError("Unexpected error in retry logic")
    
    @keyword("Retry Request On Session")
    def retry_request_on_session(self, 
                                alias: str, 
                                method: str, 
                                url: str,
                                max_retries: Optional[int] = None,
                                backoff_factor: Optional[float] = None,
                                retry_on_status: Optional[Union[str, List[int]]] = None,
                                expected_status=None,
                                msg=None,
                                **kwargs) -> Response:
        """
        Performs HTTP request with custom retry logic on a session.
        
        Args:
            alias: Session alias name
            method: HTTP method (GET, POST, PUT, etc.)
            url: Request URL
            max_retries: Override max retries for this request
            backoff_factor: Override backoff factor for this request
            retry_on_status: Override retry status codes for this request
            expected_status: Expected HTTP status code
            msg: Custom error message
            **kwargs: Additional request parameters
        
        Returns:
            HTTP Response object
        
        Examples:
        | ${response}= | Retry Request On Session | my_session | GET | /api/data |
        | ${response}= | Retry Request On Session | my_session | POST | /api/submit | max_retries=5 |
        | ${response}= | Retry Request On Session | my_session | GET | /api/flaky | retry_on_status=500,503 |
        """
        session = self._cache.switch(alias)
        
        # Get base retry config and create a copy to avoid modifying the original
        base_config = self._get_retry_config(alias)
        retry_config = RetryConfig(
            max_retries=base_config.max_retries,
            backoff_factor=base_config.backoff_factor,
            backoff_max=base_config.backoff_max,
            retry_on_status=base_config.retry_on_status.copy(),
            retry_on_exceptions=base_config.retry_on_exceptions.copy(),
            jitter=base_config.jitter
        )
        
        # Override with request-specific parameters (convert types as needed)
        if max_retries is not None:
            retry_config.max_retries = int(max_retries)
        if backoff_factor is not None:
            retry_config.backoff_factor = float(backoff_factor)
        if retry_on_status is not None:
            if isinstance(retry_on_status, str):
                retry_config.retry_on_status = [int(code.strip()) for code in retry_on_status.split(',')]
            else:
                retry_config.retry_on_status = retry_on_status
        
        # Get the method function from session
        method_func = getattr(session, method.lower())
        
        # Execute with retry
        response = self._execute_with_retry(
            method_func,
            retry_config,
            self._get_url(session, url),
            **kwargs
        )
        
        # Check expected status if provided
        if expected_status is not None:
            self._check_status(expected_status, response, msg)
        
        return response
    
    @keyword("Wait Until Request Succeeds")
    def wait_until_request_succeeds(self,
                                   alias: str,
                                   method: str,
                                   url: str,
                                   timeout: float = 60.0,
                                   interval: float = 1.0,
                                   expected_status: Union[int, str] = 200,
                                   **kwargs) -> Response:
        """
        Repeatedly makes HTTP requests until it succeeds or timeout is reached.
        
        Args:
            alias: Session alias name
            method: HTTP method (GET, POST, PUT, etc.)
            url: Request URL
            timeout: Maximum time to wait in seconds (default: 60.0)
            interval: Time between attempts in seconds (default: 1.0)
            expected_status: Expected HTTP status code (default: 200)
            **kwargs: Additional request parameters
        
        Returns:
            HTTP Response object when successful
        
        Examples:
        | ${response}= | Wait Until Request Succeeds | my_session | GET | /health |
        | ${response}= | Wait Until Request Succeeds | my_session | GET | /api/ready | timeout=120 | interval=5 |
        """
        # Convert parameters to correct types (Robot Framework passes everything as strings)
        timeout = float(timeout)
        interval = float(interval)
        if isinstance(expected_status, str) and expected_status.isdigit():
            expected_status = int(expected_status)
        
        session = self._cache.switch(alias)
        method_func = getattr(session, method.lower())
        
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            try:
                response = method_func(self._get_url(session, url), **kwargs)
                
                # Check if status matches expected
                if isinstance(expected_status, int):
                    if response.status_code == expected_status:
                        logger.info(f"Request succeeded on attempt {attempt} after {time.time() - start_time:.2f} seconds")
                        return response
                elif isinstance(expected_status, str):
                    if expected_status.lower() in ['any', 'anything']:
                        logger.info(f"Request completed on attempt {attempt} after {time.time() - start_time:.2f} seconds")
                        return response
                    elif response.status_code == int(expected_status):
                        logger.info(f"Request succeeded on attempt {attempt} after {time.time() - start_time:.2f} seconds")
                        return response
                
                logger.debug(f"Attempt {attempt}: Got status {response.status_code}, expected {expected_status}")
                
            except Exception as e:
                logger.debug(f"Attempt {attempt}: Request failed with {type(e).__name__}: {str(e)}")
            
            if time.time() - start_time + interval < timeout:
                time.sleep(interval)
            else:
                break
        
        raise TimeoutError(f"Request did not succeed within {timeout} seconds after {attempt} attempts")
