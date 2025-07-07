# Enhanced Retry Mechanisms

HttpxLibrary provides comprehensive retry mechanisms to handle transient failures and improve the reliability of HTTP requests. This feature addresses the lack of built-in retry functionality in the httpx library.

## Features

### 1. Global Retry Configuration
Set default retry behavior for all HTTP requests:

```robotframework
Set Global Retry Configuration    max_retries=5    backoff_factor=0.5    retry_on_status=500,502,503,504,429
```

### 2. Session-Specific Retry Configuration
Override global settings for specific sessions:

```robotframework
Create Session    api_session    https://api.example.com
Set Session Retry Configuration    api_session    max_retries=10    backoff_factor=1.0
```

### 3. Request-Level Retry Parameters
Override retry settings for individual requests:

```robotframework
${response}=    GET On Session With Retry    api_session    /endpoint    max_retries=3    retry_on_status=429,503
```

### 4. Flexible Retry Logic
- **Exponential Backoff**: Configurable backoff factor with optional jitter
- **Status Code Based**: Retry on specific HTTP status codes
- **Exception Based**: Retry on connection errors, timeouts, etc.
- **Maximum Backoff**: Configurable maximum wait time between retries

## Available Keywords

### Configuration Keywords

#### `Set Global Retry Configuration`
Sets the default retry configuration for all HTTP requests.

**Parameters:**
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `backoff_factor` (float): Backoff factor for exponential backoff (default: 0.3)
- `backoff_max` (float): Maximum backoff time in seconds (default: 120.0)
- `retry_on_status` (str/list): HTTP status codes to retry on (default: "500,502,503,504,429")
- `jitter` (bool): Whether to add random jitter to backoff times (default: True)

#### `Set Session Retry Configuration`
Sets retry configuration for a specific session.

**Parameters:**
- `alias` (str): Session alias name
- Same parameters as `Set Global Retry Configuration`

#### `Get Retry Configuration`
Returns the current retry configuration.

**Parameters:**
- `alias` (str, optional): Session alias name. If None, returns global configuration.

#### `Clear Session Retry Configuration`
Clears session-specific retry configuration, falling back to global settings.

**Parameters:**
- `alias` (str): Session alias name

### Request Keywords

#### `Retry Request On Session`
Performs HTTP request with custom retry logic.

**Parameters:**
- `alias` (str): Session alias name
- `method` (str): HTTP method (GET, POST, PUT, etc.)
- `url` (str): Request URL
- `max_retries` (int, optional): Override max retries for this request
- `backoff_factor` (float, optional): Override backoff factor for this request
- `retry_on_status` (str/list, optional): Override retry status codes for this request
- `expected_status`: Expected HTTP status code
- `msg`: Custom error message
- `**kwargs`: Additional request parameters

#### HTTP Method Keywords with Retry
All standard HTTP methods have retry-enabled versions:
- `GET On Session With Retry`
- `POST On Session With Retry`
- `PUT On Session With Retry`
- `PATCH On Session With Retry`
- `DELETE On Session With Retry`

#### `Wait Until Request Succeeds`
Repeatedly makes HTTP requests until success or timeout.

**Parameters:**
- `alias` (str): Session alias name
- `method` (str): HTTP method
- `url` (str): Request URL
- `timeout` (float): Maximum time to wait in seconds (default: 60.0)
- `interval` (float): Time between attempts in seconds (default: 1.0)
- `expected_status`: Expected HTTP status code (default: 200)
- `**kwargs`: Additional request parameters

## Usage Examples

### Basic Usage

```robotframework
*** Settings ***
Library    HttpxLibrary

*** Test Cases ***
Basic Retry Example
    # Create session
    Create Session    api    https://api.example.com
    
    # Configure global retry settings
    Set Global Retry Configuration    max_retries=5    backoff_factor=0.5
    
    # Make request with retry
    ${response}=    GET On Session With Retry    api    /data
    Should Be Equal As Integers    ${response.status_code}    200
```

### Advanced Configuration

```robotframework
*** Test Cases ***
Advanced Retry Configuration
    Create Session    flaky_api    https://flaky-service.com
    
    # Configure session-specific retry behavior
    Set Session Retry Configuration    flaky_api
    ...    max_retries=10
    ...    backoff_factor=1.0
    ...    retry_on_status=429,500,502,503,504
    ...    jitter=True
    
    # Make request with custom retry parameters
    ${response}=    POST On Session With Retry    flaky_api    /submit
    ...    json=${data}
    ...    max_retries=3
    ...    retry_on_status=429,503
    
    Should Be Equal As Integers    ${response.status_code}    201
```

### Health Check Pattern

```robotframework
*** Test Cases ***
Wait For Service To Be Ready
    Create Session    health    https://service.example.com
    
    # Wait until service is healthy
    ${response}=    Wait Until Request Succeeds
    ...    health    GET    /health
    ...    timeout=120    interval=5    expected_status=200
    
    Log    Service is ready!
```

### Error Handling

```robotframework
*** Test Cases ***
Handle Transient Failures
    Create Session    api    https://api.example.com
    
    # Configure to retry only on server errors
    Set Session Retry Configuration    api
    ...    max_retries=3
    ...    retry_on_status=500,502,503,504
    
    # This will retry on 5xx errors but not on 4xx
    Run Keyword And Expect Error    *
    ...    GET On Session With Retry    api    /not-found    expected_status=200
```

## Retry Logic Details

### Backoff Calculation
The backoff time is calculated using exponential backoff with optional jitter:

```
backoff_time = backoff_factor * (2 ** attempt_number)
if jitter:
    backoff_time *= (0.5 + random() * 0.5)
backoff_time = min(backoff_time, backoff_max)
```

### Default Retry Conditions
By default, requests are retried on:
- **HTTP Status Codes**: 500, 502, 503, 504, 429
- **Exceptions**: ConnectError, TimeoutException, RequestError

### Configuration Hierarchy
1. Request-level parameters (highest priority)
2. Session-specific configuration
3. Global configuration (lowest priority)

## Best Practices

1. **Set Reasonable Limits**: Don't set max_retries too high to avoid long delays
2. **Use Appropriate Status Codes**: Only retry on transient failures (5xx, 429)
3. **Configure Backoff**: Use exponential backoff to avoid overwhelming servers
4. **Enable Jitter**: Helps prevent thundering herd problems
5. **Set Timeouts**: Always set reasonable timeout values
6. **Monitor Retry Behavior**: Log retry attempts for debugging

## Integration with Existing Code

The retry functionality is fully backward compatible. Existing code will continue to work unchanged, and you can gradually adopt retry features where needed.

```robotframework
# Existing code - no changes needed
${response}=    GET On Session    api    /data

# Enhanced with retry - drop-in replacement
${response}=    GET On Session With Retry    api    /data
```

## Performance Considerations

- Retry mechanisms add latency in failure scenarios
- Configure appropriate timeouts to prevent excessive delays
- Use session-specific configurations for different service reliability levels
- Monitor retry metrics to optimize configuration

## Troubleshooting

### Common Issues

1. **Too Many Retries**: Reduce max_retries or check service health
2. **Long Delays**: Reduce backoff_factor or backoff_max
3. **No Retries**: Check retry_on_status configuration
4. **Unexpected Retries**: Verify status codes and exception types

### Debugging

Enable debug logging to see retry behavior:

```robotframework
Set Log Level    DEBUG
${response}=    GET On Session With Retry    api    /endpoint    max_retries=3
```

This will log retry attempts, backoff times, and failure reasons.
