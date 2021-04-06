# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!---
DO NOT DELETE
The next few lines form the template for unreleased changes.
## [Unreleased]
### Added
### Changed
### Deprecated
### Removed
### Fixed
-->

## v0.1.0

First official SDK release. Numerous changes and improvements implemented, with the goal of stabilizing the SDK
and making it broadly available to the community.

### Added

- Added this CHANGELOG.md file (#68, !43)
- Added standardized tap tests (!36, #78, !46)
- Added SDK testing matrix for python versions 3.6, 3.7, 3.8 (#61, !33)
- Added support for multiple `--config=` inputs, combining one or more config.json files (#53, !27)
- Added new CLI `--test` option to perform connection test on all defined streams (#14, !28)
- Added default value support for plugin configs (!12) -- _Contributed by: **[Ken Payne](https://gitlab.com/kgpayne)**_

### Changed

- Promote `singer_sdk.helpers.typing` to `singer_sdk.typing` (#84)
- Modified environment variable parsing logic for arrays (#82)
- Renamed `http_headers` in `Authenticator` class to `auth_headers` (#75, !47)
- Expect environment variables in all caps (`<PLUGIN>_<SETTING>`) (#59, !34)
- Parse environment variables only if `--config=ENV` is passed (#53, !27)

### Fixed

- OAuth no longer applies `client_email` automatically if `client_id` is missing (#83)
- Resolved issue on Python 3.6: `cannot import 'metadata' from 'importlib'` (#58)
- Fixed issue reading from JSON file (!11) -- _Contributed by: **[Edgar R. Mondragón](https://gitlab.com/edgarrmondragon)**_
- Look only for valid plugin settings in environment variables (!21) -- _Contributed by: **[Edgar R. Mondragón](https://gitlab.com/edgarrmondragon)**_
- Fixed bug in `STATE` handling (!13) -- _Contributed by: **[Ken Payne](https://gitlab.com/kgpayne)**_

### Removed

- Remove parquet sample (#81,!48)

## v0.0.1-devx

Initial prerelease version for review and prototyping.