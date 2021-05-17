*** Settings ***
Library  HttpxLibrary
Library  OperatingSystem
Library  base64Decode.py
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions

*** Test Cases ***

Put Request With Streaming Upload
    [Tags]  put
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  http2=${False}
    ${handle}  Get File For Streaming Upload  ${CURDIR}${/}randombytes.bin
    ${headers}  Create Dictionary  Content-Type=application/octet-stream   Accept=application/octet-stream
    ${resp}  Put On Session  http_server  /anything  data=${handle}  headers=&{headers}
    ${receivedData}  Base64 Decode Data  ${resp.json()['data']}
    ${data}  Get Binary File  ${CURDIR}${/}randombytes.bin
    Should Be Equal  ${receivedData}  ${data}

Patch Request With Streaming Upload
    [Tags]  patch
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  http2=${False}
    ${handle}  Get File For Streaming Upload  ${CURDIR}${/}randombytes.bin
    ${headers}  Create Dictionary  Content-Type=application/octet-stream   Accept=application/octet-stream
    ${resp}  Patch On Session  http_server  /anything  data=${handle}  headers=&{headers}
    ${receivedData}  Base64 Decode Data  ${resp.json()['data']}
    ${data}  Get Binary File  ${CURDIR}${/}randombytes.bin
    Should Be Equal  ${receivedData}  ${data}

Post Request With Streaming Upload
    [Tags]  post
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  http2=${False}
    ${handle}  Get File For Streaming Upload  ${CURDIR}${/}randombytes.bin
    ${headers}  Create Dictionary  Content-Type=application/octet-stream   Accept=application/octet-stream
    ${resp}  Post On Session  http_server  /anything  data=${handle}  headers=&{headers}
    ${receivedData}  Base64 Decode Data  ${resp.json()['data']}
    ${data}  Get Binary File  ${CURDIR}${/}randombytes.bin
    Should Be Equal  ${receivedData}  ${data}
