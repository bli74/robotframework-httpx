*** Settings ***
Library  String
Library  Collections
Library  HttpxLibrary
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions


*** Variables ***
${HTTP_LOCAL_SERVER}    http://localhost:5000


*** Test Cases ***
Retry Get Request Because Of 502 Error With Default Config
    [Tags]  get  retry
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  http2=${False}
    Run Keyword And Expect Error  HTTPStatusError: *502 *   Get On Session  http_server  /status/502

Retry Get Request Because Of 502 Error With Max Retries 1
    [Tags]  get  retry
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  retries=1  http2=${False}
    Run Keyword And Expect Error  HTTPStatusError: *502 *   Get On Session  http_server  /status/502

Retry Disabled Get Request
    [Tags]  get  retry
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  retries=0  http2=${False}
    Get On Session  http_server  /status/502  expected_status=502

# TODO fake the server in order to recover after a while
