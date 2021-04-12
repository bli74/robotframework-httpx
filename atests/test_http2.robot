*** Settings ***
Library  Collections
Library  String
Library  HttpxLibrary
Library  OperatingSystem
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions

*** Variables ***
${test_session}     local test session created in Test Setup

*** Test Cases ***
Get Requests
    Create Session    http2_demo  https://http2.akamai.com
    GET On Session    http2_demo  demo


