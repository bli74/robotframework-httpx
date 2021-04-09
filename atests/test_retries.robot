*** Settings ***
Library  String
Library  Collections
Library  HttpxLibrary
Resource  res_setup.robot

Suite Setup     Setup Flask Http Server
Suite Teardown  Teardown Flask Http Server And Sessions


*** Variables ***
${HTTP_LOCAL_SERVER}    http://localhost:5000


*** Test Cases ***
Retry Get Request Because Of 502 Error With Default Config
    [Tags]  get  retry
    ${retry_status_list}=   Create List  502  503
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  http2=False
    Run Keyword And Expect Error  RetryError: *   Get Request  http_server  /status/502

Retry Get Request Because Of 502 Error With Max Retries 1
    [Tags]  get  retry
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  max_retries=1  http2=False
    Run Keyword And Expect Error  RetryError: *   Get Request  http_server  /status/502

Retry Disabled Get Request
    [Tags]  get  retry
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  max_retries=0  http2=False
    Get Request  http_server  /status/502

# TODO fake the server in order to recover after a while
