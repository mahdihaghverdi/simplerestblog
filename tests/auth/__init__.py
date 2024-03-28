"""Testing the Authentication and Authorization of the applications

What to test:
    1. /signup
    2. /login
    3. /2fa-img
    4. /verify
    5. /refresh
    6. /logout

Test scenarios:
    1. /signup
        - Successful signup with no optional data
        - Successful signup with all the data
        - Unsuccessful signup due to `DuplicateUsernameError`

    2. /login
        - Unsuccessful login due to `UserNotFoundError`
        - Unsuccessful login due to `CredentialsError`
        - Successful login
            get the Refresh-Token from cookies
            get the X-CSRF-TOKEN from headers

    3. /2fa-img
        - Unsuccessful due to not passing the Refresh-Token (`ForbiddenError`)
        - Unsuccessful due to invalid Refresh-Token passing (`CredentialsError`)
        - Successful generation
            get the image and test it

    4. /verify
        - Unsuccessful due to not passing the Refresh-Token (`ForbiddenError`)
        - Unsuccessful due to invalid Refresh-Token passing (`CredentialsError`)
        - Unsuccessful due to Invalid totp code (`CredentialsError`)
        - Successful
            test it is set the redis

    5. /refresh
        - Unsuccessful due to not passing the Refresh-Token (`ForbiddenError`)
        - Unsuccessful due to invalid Refresh-Token passing (`CredentialsError`)
        - Unsuccessful due to not verifying two-step authentication
        - Successful
            get the Refresh-Token
            get the Access-Token
            get X-CSRF-TOKEN
        - Repeat successful

    6. /logout
        - Unsuccessful due to not providing the Access-Token (`ForbiddenError`)
        - Unsuccessful due to wrong Access-Token (`CredentialsError`)
        - Successful
            test refresh is deleted from redis
            test sha256_username is deleted from redis

    7. /users/me (Just test the Access-Token)
        - Unsuccessful due to not providing the Access-Token (`ForbiddenError`)
        - Unsuccessful due to wrong Access-Token (`CredentialsError`)
        - Successful
            test the user info
"""
