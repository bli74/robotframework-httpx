🏠 ``HttpxLibrary`` is a [Robot Framework](https://robotframework.org/) library
aimed to provide HTTP api testing functionalities by wrapping the well known [Python httpx Library](https://www.python-httpx.org/).
It is based on [robotframework-requests Library](https://github.com/MarketSquare/robotframework-requests) but
uses *httpx* library with HTTP/2 support instead of *requests* library.

## Key Features

- **HTTP/2 Support**: Native HTTP/2 support through httpx
- **Enhanced Retry Mechanisms**: Comprehensive retry functionality with exponential backoff
- **Session Management**: Full session support with custom configurations
- **Modern Architecture**: Built on the modern httpx library
- **Backward Compatibility**: Drop-in replacement for robotframework-requests

## Install stable version
```sh
pip install robotframework-httpx
```

## 🤖 Example usage
```robotframework
*** Settings ***
Library               Collections
Library               HttpxLibrary

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

Retry Request Test
    # Configure retry behavior
    Set Global Retry Configuration      max_retries=5    backoff_factor=0.5
    
    # Make request with retry on failure
    ${resp}=          GET On Session With Retry    jsonplaceholder    /posts/1    max_retries=3
    Status Should Be                     200    ${resp}
```

## 🔄 Enhanced Retry Mechanisms

HttpxLibrary provides comprehensive retry functionality to handle transient failures:

```robotframework
# Configure global retry settings
Set Global Retry Configuration    max_retries=5    backoff_factor=0.5    retry_on_status=500,502,503

# Session-specific retry configuration
Set Session Retry Configuration    my_session    max_retries=10    backoff_factor=1.0

# HTTP methods with retry support
${response}=    GET On Session With Retry     my_session    /api/data    max_retries=3
${response}=    POST On Session With Retry    my_session    /api/submit    json=${data}

# Wait until service is ready
${response}=    Wait Until Request Succeeds    my_session    GET    /health    timeout=60
```

See [RETRY_FEATURES.md](RETRY_FEATURES.md) for detailed documentation.

### 📖 Keywords documentation
robotframework-httpx offers a wide set of keywords which can be found in the Keywords documentation

### 🔬 Test examples
You can find many test examples inside the `atests` folder.

## 🤝 Contributing ✍️
Feel free to contribute and open an issue in order to discuss it. Before doing it take a look at the [contribution guidelines](CONTRIBUTING.md).

