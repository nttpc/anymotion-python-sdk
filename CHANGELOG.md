# Change Log

## 1.1.0

Unreleased

- Added `Client.download_and_read` method that can be used by installing the extra package.
- Changed the return value of `Client.download` to the path downloaded from None.
- Changed to refresh token before they expire.
- Moved the token property from the Client class to the Authentication class.

## 1.0.1

Released 2020-05-06

- Fixed a bug that caused duplicate query parameters in requests for the next URL.

## 1.0.0

Released 2020-04-27

- Public release.

## 0.2.1

Released 2020-03-10

- Changed from automatic to optional about correct the extension.

## 0.2.0

Released 2020-03-06

- Added to retry when server error occurs in HTTP request.
- Changed to automatically correct the extension when downloading.

## 0.1.1

Released 2020-02-28

- Fixed upload bug when text is None.

## 0.1.0

Released 2020-02-26

- Initial release.
