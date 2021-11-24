*** Settings ***
Library  Collections
Library  String
Library  HttpxLibrary
Library  OperatingSystem
Suite Teardown  Delete All Sessions

*** Test Cases ***
Post Request With XML File
    [Tags]  post
    Create Session  httpbin  http://httpbin.org    http2=False

    ${file_data}=  Get Binary File  ${CURDIR}${/}test.xml
    ${files}=  Create Dictionary  xml=${file_data}
    ${headers}=  Create Dictionary  Authorization=testing-token
    Log  ${headers}
    ${resp}=  Post On Session  httpbin  /post  files=${files}  headers=${headers}

    Log  ${resp.json()}

    Set Test Variable  ${req_headers}  ${resp.json()['headers']}

    Dictionary Should Contain Key  ${req_headers}  Authorization
