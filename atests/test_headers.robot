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
Get Request With Session Headers
    [Tags]  get  headers
    ${sess_headers}     Create Dictionary  session-header=true
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  headers=${sess_headers}    http2=False
    ${resp}  Get On Session  http_server  /headers
    Dictionary Should Contain Item  ${resp.json()['headers']}  Session-Header  true

Get Request Overriding Session Headers
    [Tags]  get  headers
    ${sess_headers}     Create Dictionary  session-header=true
    ${get_headers}      Create Dictionary  session-header=false
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  headers=${sess_headers}    http2=False
    ${resp}  Get On Session  http_server  /headers  headers=${get_headers}
    Dictionary Should Contain Item  ${resp.json()['headers']}  Session-Header  false

Get Request Headers Are Local
    [Tags]  get  headers
    ${sess_headers}     Create Dictionary  session-header=true
    ${get_headers}      Create Dictionary  session-header=false
    Create Session  http_server  ${HTTP_LOCAL_SERVER}  headers=${sess_headers}    http2=False
    ${resp1}  Get On Session  http_server  /headers  headers=${get_headers}
    Dictionary Should Contain Item  ${resp1.json()['headers']}  Session-Header  false
    ${resp2}  Get On Session  http_server  /headers
    Dictionary Should Contain Item  ${resp2.json()['headers']}  Session-Header  true
