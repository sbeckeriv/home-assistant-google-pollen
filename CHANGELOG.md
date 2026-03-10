# Changelog

All notable changes to this fork will be documented in this file.

## [0.36.0] - 2026-03-09

### Added
- New `google_pollen.get_pollen_forecast` service for querying pollen data at any latitude/longitude
- Service allows location-based automations using phone GPS coordinates
- Comprehensive service usage examples in SERVICE_EXAMPLES.md
- Support for querying 1-5 days of forecast data
- Service returns full API response for use in templates and automations

### Changed
- Updated for Home Assistant 2024.1.0+ compatibility
- Migrated from deprecated `Entity` to `SensorEntity`
- Changed `state` property to `native_value`
- Converted hacs.json to info.json format
- Updated minimum Home Assistant version requirement to 2024.1.0
- Updated manifest.json to point to fork repository
- Updated README to indicate fork and highlight new features

### Improved
- Added comprehensive type hints throughout codebase (`from __future__ import annotations`)
- Improved error handling using `UpdateFailed` exceptions in coordinator
- Fixed reconfigure flow to properly update configuration
- Removed invalid `device_class` and `state_class` attributes from sensors
- Removed unused `PLATFORM_SCHEMA` (config flow only)
- Full type annotations on all functions and methods
- Better code formatting and consistency

### Documentation
- Added SERVICE_EXAMPLES.md with automation examples
- Updated README with service documentation
- Added "What's New in This Fork" section to README
- Included credits to original author

## Original Version History

This fork is based on [svenove/home-assistant-google-pollen](https://github.com/svenove/home-assistant-google-pollen) v0.32.0.

For the original version history, see the [upstream repository](https://github.com/svenove/home-assistant-google-pollen/releases).
