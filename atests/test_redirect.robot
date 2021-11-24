*** Settings ***
Library   HttpxLibrary
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions

*** Test Cases ***
Get Request With Default Redirection
    [Tags]  get
    ${resp}  Get On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything    follow_redirects=${True}
    Status Should Be  OK  ${resp}
    Length Should Be  ${resp.history}  1

Get Request With Redirection
    [Tags]  get
    ${resp}  Get On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${True}
    Status Should Be  OK  ${resp}
    Length Should Be  ${resp.history}  1

Get Request Without Redirection
    [Tags]  get
    ${resp}  Get On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything   expected_status=302
    Status Should Be  302  ${resp}
    Length Should Be  ${resp.history}  0

# TODO understand whether this is the right behavior or not
Options Request Without Redirection By Default
    [Tags]  options
    ${resp}  Options On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything
    Status Should Be  OK  ${resp}
    Length Should Be  ${resp.history}  0

# TODO understand whether this is the right behavior or not
Options Request With Redirection
    [Tags]  options
    ${resp}  Options On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${true}
    Status Should Be  OK  ${resp}
    Length Should Be  ${resp.history}  0

Head Request With Redirection
    [Tags]  head
    ${resp}  Head On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${true}
    Status Should Be  OK  ${resp}
    Length Should Be  ${resp.history}  1

Head Request Without Redirection
    ${resp}  Head On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${false}   expected_status=302
    ${status}  Convert To String  ${resp.status_code}
    Status Should Be  302  ${resp}
    Length Should Be  ${resp.history}  0

Post Request With Redirection
    [Tags]  post
    # FIXME should be 2 different tests
    # FIXME should be verifed also the payload is returned
    # FIXME returned http method should be verified
    ${resp}  Post On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  data=something  follow_redirects=${true}
    Status Should be  OK  ${resp}
    ${redirected_url}  Catenate  ${HTTP_LOCAL_SERVER}/anything
    Should Be Equal As Strings  ${resp.json()['url']}  ${redirected_url}

Post Request Without Redirection
    [Tags]  post
    ${resp}  Post On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  data=something  follow_redirects=${false}   expected_status=302
    Status Should be  302  ${resp}

Put Request With Redirection
    [Tags]  put
    # FIXME should be 2 different tests
    # FIXME should be verifed also the payload is returned
    # FIXME returned http method should be verified
    ${resp}  Put On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${true}
    Status Should be  OK  ${resp}
    ${redirected_url}  Catenate  ${HTTP_LOCAL_SERVER}/anything
    Should Be Equal As Strings  ${resp.json()['url']}  ${redirected_url}

Put Request Without Redirection
    [Tags]  put
    ${resp}  Put On Session  ${GLOBAL_SESSION}  url=/redirect-to?url=anything  follow_redirects=${false}   expected_status=302
    Status Should be  302  ${resp}
