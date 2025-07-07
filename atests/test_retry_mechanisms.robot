*** Settings ***
Library               Collections
Library               HttpxLibrary
Library               OperatingSystem

Suite Setup           Setup Test Environment
Suite Teardown        Teardown Test Environment

*** Variables ***
${BASE_URL}           http://httpbin.org
${FLAKY_URL}          http://httpbin.org/status/500,200
${TIMEOUT_URL}        http://httpbin.org/delay/2

*** Test Cases ***

Test Global Retry Configuration
    [Documentation]    Test setting and getting global retry configuration
    Set Global Retry Configuration    max_retries=5    backoff_factor=0.5    retry_on_status=500,502,503
    ${config}=    Get Retry Configuration
    Should Be Equal As Integers    ${config}[max_retries]    5
    Should Be Equal As Numbers     ${config}[backoff_factor]    0.5
    Should Contain    ${config}[retry_on_status]    500
    Should Contain    ${config}[retry_on_status]    502
    Should Contain    ${config}[retry_on_status]    503

Test Session Retry Configuration
    [Documentation]    Test setting session-specific retry configuration
    Create Session    test_session    ${BASE_URL}
    Set Session Retry Configuration    test_session    max_retries=3    backoff_factor=1.0
    ${config}=    Get Retry Configuration    test_session
    Should Be Equal As Integers    ${config}[max_retries]    3
    Should Be Equal As Numbers     ${config}[backoff_factor]    1.0

Test Clear Session Retry Configuration
    [Documentation]    Test clearing session retry configuration
    Create Session    clear_session    ${BASE_URL}
    Set Session Retry Configuration    clear_session    max_retries=10
    ${config_before}=    Get Retry Configuration    clear_session
    Should Be Equal As Integers    ${config_before}[max_retries]    10
    
    Clear Session Retry Configuration    clear_session
    ${config_after}=    Get Retry Configuration    clear_session
    # Should fall back to global configuration
    Should Be Equal As Integers    ${config_after}[max_retries]    5

Test Retry Request On Session Success
    [Documentation]    Test successful request with retry mechanism
    Create Session    retry_session    ${BASE_URL}
    ${response}=    Retry Request On Session    retry_session    GET    /get
    Should Be Equal As Integers    ${response.status_code}    200
    Should Contain    ${response.text}    "url"

Test Retry Request On Session With Custom Parameters
    [Documentation]    Test retry request with custom retry parameters
    Create Session    custom_session    ${BASE_URL}
    ${response}=    Retry Request On Session    custom_session    GET    /get    
    ...    max_retries=2    backoff_factor=0.1    retry_on_status=404,500
    Should Be Equal As Integers    ${response.status_code}    200

Test GET On Session With Retry
    [Documentation]    Test GET request with retry functionality
    Create Session    get_retry_session    ${BASE_URL}
    ${response}=    GET On Session With Retry    get_retry_session    /get    max_retries=3
    Should Be Equal As Integers    ${response.status_code}    200
    Should Contain    ${response.text}    "url"

Test POST On Session With Retry
    [Documentation]    Test POST request with retry functionality
    Create Session    post_retry_session    ${BASE_URL}
    &{data}=    Create Dictionary    key=value    test=data
    ${response}=    POST On Session With Retry    post_retry_session    /post    
    ...    json=${data}    max_retries=2
    Should Be Equal As Integers    ${response.status_code}    200
    Should Contain    ${response.text}    "key"

Test PUT On Session With Retry
    [Documentation]    Test PUT request with retry functionality
    Create Session    put_retry_session    ${BASE_URL}
    &{data}=    Create Dictionary    update=true
    ${response}=    PUT On Session With Retry    put_retry_session    /put    
    ...    json=${data}    max_retries=2
    Should Be Equal As Integers    ${response.status_code}    200

Test PATCH On Session With Retry
    [Documentation]    Test PATCH request with retry functionality
    Create Session    patch_retry_session    ${BASE_URL}
    &{data}=    Create Dictionary    patch=true
    ${response}=    PATCH On Session With Retry    patch_retry_session    /patch    
    ...    json=${data}    max_retries=2
    Should Be Equal As Integers    ${response.status_code}    200

Test DELETE On Session With Retry
    [Documentation]    Test DELETE request with retry functionality
    Create Session    delete_retry_session    ${BASE_URL}
    ${response}=    DELETE On Session With Retry    delete_retry_session    /delete    max_retries=2
    Should Be Equal As Integers    ${response.status_code}    200

Test Wait Until Request Succeeds
    [Documentation]    Test waiting until request succeeds
    Create Session    wait_session    ${BASE_URL}
    ${response}=    Wait Until Request Succeeds    wait_session    GET    /get    
    ...    timeout=30    interval=1    expected_status=200
    Should Be Equal As Integers    ${response.status_code}    200

Test Wait Until Request Succeeds With Any Status
    [Documentation]    Test waiting until request succeeds with any status
    Create Session    wait_any_session    ${BASE_URL}
    ${response}=    Wait Until Request Succeeds    wait_any_session    GET    /status/404    
    ...    timeout=10    interval=1    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    404

Test Retry With Different Status Codes
    [Documentation]    Test retry behavior with different HTTP status codes
    Create Session    status_session    ${BASE_URL}
    Set Session Retry Configuration    status_session    max_retries=1    retry_on_status=404
    
    # This should not retry (200 is not in retry_on_status)
    ${response}=    Retry Request On Session    status_session    GET    /status/200
    Should Be Equal As Integers    ${response.status_code}    200
    
    # This should retry once but still fail (404 is in retry_on_status)
    Run Keyword And Expect Error    *    
    ...    Retry Request On Session    status_session    GET    /status/404    expected_status=200

Test Retry Configuration Inheritance
    [Documentation]    Test that session config overrides global config
    # Set global config
    Set Global Retry Configuration    max_retries=2    backoff_factor=0.2
    
    # Create session without specific config (should use global)
    Create Session    inherit_session    ${BASE_URL}
    ${global_config}=    Get Retry Configuration    inherit_session
    Should Be Equal As Integers    ${global_config}[max_retries]    2
    
    # Set session-specific config (should override global)
    Set Session Retry Configuration    inherit_session    max_retries=7
    ${session_config}=    Get Retry Configuration    inherit_session
    Should Be Equal As Integers    ${session_config}[max_retries]    7

*** Keywords ***

Setup Test Environment
    [Documentation]    Setup test environment
    Log    Setting up test environment for retry mechanisms
    # Reset to default global configuration
    Set Global Retry Configuration    max_retries=3    backoff_factor=0.3

Teardown Test Environment
    [Documentation]    Cleanup test environment
    Log    Cleaning up test environment
    Delete All Sessions
