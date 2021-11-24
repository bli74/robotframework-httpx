*** Settings ***
Library  HttpxLibrary
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions


*** Test Cases ***

Request And Status Should Be Different
    [Tags]  get  status
    Run Keyword And Expect Error  Url: http://localhost:5000/status/404 Expected status: 404 != 201
    ...  Get On Session  ${GLOBAL_SESSION}  /status/404  expected_status=201

Request And Status Should Be Equal
    [Tags]  get  status
    ${resp}  Get On Session  ${GLOBAL_SESSION}  /status/404  expected_status=404
    Status Should Be  404  ${resp}

Request And Status Should Be A Named Status Code
    [Tags]  get  status
    ${resp}  Get On Session  ${GLOBAL_SESSION}  /status/404  expected_status=NOT FOUND
    Status Should Be  NOT FOUND  ${resp}

Request And Status Should Be An Unknown Named Status
    [Tags]  get  status
    Run Keyword And Expect Error    KeyError: 'NONEXISTENT'
    ...  Get On Session  ${GLOBAL_SESSION}  /status/404  expected_status=NONEXISTENT

Invalid Response
    [Tags]  get  status
    Run Keyword And Expect Error  InvalidResponse: this-is-not-a-response*
    ...  Status Should Be  123   this-is-not-a-response

Request And Status Should Be With A Message
    [Tags]  get  status
    Run Keyword And Expect Error  Url: http://localhost:5000/status/418 Expected status: 418 != 200
    ...   Get On Session  ${GLOBAL_SESSION}  /status/418  expected_status=200

Request Should Be Successful
    [Tags]  get  status
    ${resp}  Get On Session  ${GLOBAL_SESSION}  /status/200
    Request Should Be Successful  ${resp}

Request Should Not Be Successful
    [Tags]  get  status
    ${resp}  Get On Session  ${GLOBAL_SESSION}  /status/500  expected_status=500
    Run Keyword And Expect Error  HTTPStatusError: *500 *  Request Should Be Successful  ${resp}

Request And Status Should Be An Invalid Expected Status
    [Tags]  get  status
    ${invalid_expected_status}     Create Dictionary  a=1
    ${resp}  Get On Session  ${GLOBAL_SESSION}  /status/500  expected_status=500
    Run Keyword And Expect Error   InvalidExpectedStatus*  Status Should Be  ${invalid_expected_status}  ${resp}
