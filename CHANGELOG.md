# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Log collection system for all Docker containers
- `collect-logs.sh` script to gather container logs into `./logs/` directory
- Log rotation configuration (10MB max size, 3 files per container)

### Changed
- Updated `docker-compose.yml` to include logging configuration for all services
- Removed obsolete `version` field from docker-compose.yml

### Fixed
- Resolved Docker logging configuration error with unsupported `path` option