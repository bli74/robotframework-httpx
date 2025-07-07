*** Settings ***
Documentation    Example demonstrating HttpxLibrary retry mechanisms
Library          HttpxLibrary

*** Variables ***
${BASE_URL}      https://httpbin.org

*** Test Cases ***

Basic Retry Example
    [Documentation]    Basic example of using retry functionality
    
    # Create a session
    Create Session    api    ${BASE_URL}
    
    # Configure global retry settings
    Set Global Retry Configuration    max_retries=5    backoff_factor=0.5
    
    # Make a request that will succeed immediately
    ${response}=    GET On Session With Retry    api    /get
    Log    Response status: ${response.status_code}
    
    # Make a request with custom retry parameters
    ${response}=    GET On Session With Retry    api    /get    
    ...    max_retries=3    retry_on_status=500,502,503
    Log    Response with custom retry: ${response.status_code}

Advanced Retry Configuration
    [Documentation]    Advanced retry configuration example
    
    Create Session    advanced_api    ${BASE_URL}
    
    # Set session-specific retry configuration
    Set Session Retry Configuration    advanced_api    
    ...    max_retries=10    
    ...    backoff_factor=1.0    
    ...    retry_on_status=429,500,502,503,504
    
    # Check the configuration
    ${config}=    Get Retry Configuration    advanced_api
    Log    Max retries: ${config}[max_retries]
    Log    Backoff factor: ${config}[backoff_factor]
    Log    Retry on status: ${config}[retry_on_status]
    
    # Use the Retry Request On Session keyword directly
    ${response}=    Retry Request On Session    advanced_api    GET    /get
    Should Be Equal As Integers    ${response.status_code}    200

Wait Until Service Is Ready
    [Documentation]    Example of waiting until a service becomes available
    
    Create Session    health_check    ${BASE_URL}
    
    # Wait until the service responds successfully
    ${response}=    Wait Until Request Succeeds    
    ...    health_check    GET    /get    
    ...    timeout=60    interval=2    expected_status=200
    
    Log    Service is ready! Status: ${response.status_code}

Different HTTP Methods With Retry
    [Documentation]    Examples of different HTTP methods with retry
    
    Create Session    methods_api    ${BASE_URL}
    
    # GET with retry
    ${get_response}=    GET On Session With Retry    methods_api    /get
    Log    GET Response: ${get_response.status_code}
    
    # POST with retry
    &{post_data}=    Create Dictionary    message=Hello World
    ${post_response}=    POST On Session With Retry    methods_api    /post    
    ...    json=${post_data}    max_retries=3
    Log    POST Response: ${post_response.status_code}
    
    # PUT with retry
    &{put_data}=    Create Dictionary    update=true
    ${put_response}=    PUT On Session With Retry    methods_api    /put    
    ...    json=${put_data}
    Log    PUT Response: ${put_response.status_code}
    
    # DELETE with retry
    ${delete_response}=    DELETE On Session With Retry    methods_api    /delete
    Log    DELETE Response: ${delete_response.status_code}

Error Handling With Retry
    [Documentation]    Example of error handling with retry mechanisms
    
    Create Session    error_api    ${BASE_URL}
    
    # Configure to retry on specific status codes
    Set Session Retry Configuration    error_api    
    ...    max_retries=2    
    ...    retry_on_status=500,503
    
    # This will succeed immediately (200 status)
    ${success_response}=    GET On Session With Retry    error_api    /status/200
    Log    Success response: ${success_response.status_code}
    
    # This will fail after retries (404 is not in retry_on_status)
    Run Keyword And Expect Error    *
    ...    GET On Session With Retry    error_api    /status/404    expected_status=200
    
    Log    Error handling completed

*** Keywords ***

Cleanup
    [Documentation]    Cleanup sessions
    Delete All Sessions
