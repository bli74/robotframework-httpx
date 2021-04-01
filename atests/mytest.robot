*** Settings ***
Library  Collections
Library  String
Library  HttpxLibrary
Library  OperatingSystem
Library  customAuthenticator.py
Library  base64Decode.py
Library  DebugLibrary
Resource  res_setup.robot

Test Setup      Setup Test Session
Test Teardown   Teardown Test Session
Suite Setup     Setup Flask Http Server
Suite Teardown  Teardown Flask Http Server And Sessions

*** Variables ***
${test_session}     local test session created in Test Setup

*** Test Cases ***
Get Requests
    [Tags]  get    skip
    Create Session  google  http://www.google.com
    Create Session  github  https://api.github.com   verify=${CURDIR}${/}cacert.pem
    ${resp}=  Get Request  google  /
    Should Be Equal As Strings  ${resp.status_code}  200
    ${resp}=  Get Request  github  /users/bulkan
    Should Be Equal As Strings  ${resp.status_code}  200
    Dictionary Should Contain Value  ${resp.json()}  Bulkan Evcimen

