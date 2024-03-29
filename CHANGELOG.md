# Change Log

## 1.2.8

Released 2022-3-23

- Updated packages.

## 1.2.7

Released 2021-12-10

- Updated packages.

## 1.2.6

Released 2021-09-02

- Changed token access url.
- Updated packages.

## 1.2.5

Released 2021-06-24

- Updated urllib3 for security and other packages.

## 1.2.4

Released 2020-11-16

- Changed the build system to poetry-core.
- Fixed a bug that extras library was installed without the extras option.
  (Use opencv-python 4.4 or higher on all Python versions.)

## 1.2.3

Released 2020-11-09

- Added support for Python 3.9.
- Changed to use opencv-python 4.4 or higher with Python 3.7 or higher.

## 1.2.2

Released 2020-09-14

- Changed User-Agent on HTTP request to anymotion-sdk/x.y.z.

## 1.2.1

Released 2020-09-01

- Changed file download to stream processing.
- Fixed a noted issue with flake8-bugbear.
  (e.g. do not perform function calls in argument defaults.)

## 1.2.0

Released 2020-08-20

- Added `compare_keypoint`, `get_comparison`, and `get_comparisons` to be able to use AnyMotion's new feature, comparison.
- Added `background_rule` to the parameter of `draw_keypoint`.
- Added exception handling for getting token.
- Made it passible to draw comparison results using `draw_keypoint`.
- Changed the color model in `download_and_read` from BGR to RGB.
- Fixed to stop outputting binary responses in the debug log.
- Fixed opencv-python version to 4.2.

## 1.1.0

Released 2020-05-21

- Added parameters for `get_keypoint`, `get_drawing`, and `get_analysis` that can also return related data at the same time.
- Added `download_and_read` method that can be used by installing the extra package.
- Changed the return value of `download` to the path downloaded from None.
- Changed to refresh token before they expire.
- Moved the token property from the `Client` class to the `Authentication` class.

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
