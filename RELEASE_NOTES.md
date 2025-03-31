# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

* Unify Public Trades streaming and listing (to align with the proto changes in v0.5.0)
    * Removed `list_public_trades`
    * Replaced `public_trades_stream` with `receive_public_trades`
    * `receive_public_trades` now supports an optional time range (`start_time`, `end_time`)
* Update repo-config from v0.11.0 to v0.13.0

## New Features


## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
