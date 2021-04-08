*** Settings ***
Library  Collections
Library  String
Library  HttpxLibrary
Library  OperatingSystem

*** Variables ***
${test_session}     local test session created in Test Setup

*** Test Cases ***
Get Requests
    Create Session    http2_demo  https://http2.akamai.com
    GET On Session    http2_demo  demo


