*** Settings ***
Library  Collections
Library  String
Library  HttpxLibrary
Resource  res_setup.robot

Suite Setup     Run Keywords  Setup Flask Http Server
...             AND  Wait Until Http Server Is Up And Running
Suite Teardown  Teardown Flask Http Server And Sessions

*** Test Cases ***

Named URL with = symbol should not have warnings
   GET On Session  ${GLOBAL_SESSION}  url=/anything  params=a=a&b=b

Positional URL with '' should not have warnings
   GET On Session  ${GLOBAL_SESSION}  url=${Empty}
