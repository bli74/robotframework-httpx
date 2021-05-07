🏠 ``HttpxLibrary`` is a [Robot Framework](https://robotframework.org/) library
aimed to provide HTTP api testing functionalities by wrapping the well known [Python httpx Library](https://www.python-httpx.org/).
It is based on [robotframework-requests Library](https://github.com/MarketSquare/robotframework-requests) but
uses *httpx* library with HTTP/2 support instead of *requests* library.

## Install stable version
```sh
pip install robotframework-httpx
```

## 🤖 Example usage
```robotframework
*** Settings ***
Library               Collections
Library               RequestsLibrary

Suite Setup           Create Session    jsonplaceholder    https://jsonplaceholder.typicode.com

*** Test Cases ***

Get Request Test
    Create Session    google             http://www.google.com

    ${resp_google}=   GET On Session     google             /           expected_status=200
    ${resp_json}=     GET On Session     jsonplaceholder    /posts/1

    Should Be Equal As Strings           ${resp_google.reason}    OK
    Dictionary Should Contain Value      ${resp_json.json()}    sunt aut facere repellat provident occaecati excepturi optio reprehenderit

Post Request Test
    &{data}=          Create dictionary  title=Robotframework requests  body=This is a test!  userId=1
    ${resp}=          POST On Session    jsonplaceholder     /posts    json=${data}
    
    Status Should Be                     201    ${resp}
    Dictionary Should Contain Key        ${resp.json()}     id
```

### 📖 Keywords documentation
robotframework-httpx offers a wide set of keywords which can be found in the Keywords documentation

### 🔬 Test examples
You can find many test examples inside the `atests` folder.

## 🤝 Contributing ✍️
Feel free to contribute and open an issue in order to discuss it. Before doing it take a look at the [contribution guidelines](CONTRIBUTING.md).

