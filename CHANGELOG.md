# Filestack-Python Changelog

### 4.0.0 (September 17th, 2024)
- Compatibility fix for AWS Lambda with Python 3.11 [#73](https://github.com/filestack/filestack-python/pull/73)
- A bunch of transform features added [#74](https://github.com/filestack/filestack-python/pull/75)
- Bumped requests lib version from 2.25.1 to >=2.31.0 [#75](https://github.com/filestack/filestack-python/pull/75)

### 3.5.0 (September 17th, 2021)
- Broaden pinned requests version from 2.24.0 to >=2.25.1 [#61](https://github.com/filestack/filestack-python/pull/61)
- Use Client's storage when uploading external urls [#62](https://github.com/filestack/filestack-python/pull/62)

### 3.4.0 (May 13th, 2021)
- Store upload response in Filelink object [#59](https://github.com/filestack/filestack-python/pull/59)

### 3.3.0 (March 12th, 2021)
- Added Image OCR [#52](https://github.com/filestack/filestack-python/pull/52)
- Changed how files from external urls are uploaded [#54](https://github.com/filestack/filestack-python/pull/54)
- Added custom exception for HTTP errors [#57](https://github.com/filestack/filestack-python/pull/57)

### 3.2.1 (July 22nd, 2020)
- FS-7797 changed http method used when uploading external urls

### 3.2.0 (June 2nd, 2020)
- Added upload tags

### 3.1.0 (April 14th, 2020)
- Transformations added: auto_image, minify_js, minify_css
- Added configurable CNAME
- Fixed path param in store task

### 3.0.1 (July 22nd, 2019)
- Added enhance presets
- Set filelink security when uploading from url

### 3.0.0 (July 16th, 2019)
- Dropped support for Python 2.7
- client.upload() now handles local files and file-like objects, accepts keyword arguments only
- client.upload_url() handles external url uploads
- Please see [API Reference](https://filestack-python.readthedocs.io) to learn more

### 2.8.1 (July 3th, 2019)
- Fixed store params in external url upload

### 2.8.0 (June 17th, 2019)
- Simplified FII uploads
- Updated uploads to use JSON-based API

### 2.7.0 (May 30th, 2019)
- Refactored and renamed webhook verification method
- Added new transformation tasks: callbak, pdf_info and pdf_convert

### 2.6.0 (May 29th, 2019)
- Added webhook signature verification

### 2.5.0 (May 20th, 2019)
- Added support for [Filestack Workflows](https://www.filestack.com/products/workflows/)

### 2.4.0 (March 18th, 2019)
- Added default mimetype for multipart uploads
- Refactored multipart uploads

### 2.3.0 (August 22th, 2017)
- FS-1556 Add SDK reference
- FS-1399 added intelligent ingestion 

### 2.2.1 (July 19th, 2017)
- FS-1364 Add all response data to AudioVisual class

### 2.1.1 (July 7th, 2017)
- FS-1365 Fix security formatting for non-transform URLs
- Add generic error handling to make_call utility function

### 2.1.0 (June 26th, 2017)
- FS-1134 Add autotagging and SFW detection 
- FS-1117 Mulipart upload now sends user parameters 
- FS-1116 Upload parameters are now optional 
- Fixes to security and mulipart uploads

### 2.0.4
- FS-1116 Make upload parameters all optional
- FS-1117 Ensure params are being sent during multipart upload

### 2.0.2 - 2.0.3
- Modify setup.py for PyPi deployment

### 2.0.1
- Modify setup.py for PyPi deployment

### 2.0.0 (June 1, 2017)
- Updated to new version, including transformations and multipart uploads

