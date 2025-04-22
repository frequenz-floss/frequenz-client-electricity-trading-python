# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

* Unify Public Trades streaming and listing (to align with the proto changes in v0.5.0)
    * Removed `list_public_trades`
    * Replaced `public_trades_stream` with `receive_public_trades`
    * `receive_public_trades` now supports an optional time range (`start_time`, `end_time`)
* Update the `frequenz-api-electricity-trading` from >= 0.5.0, < 0.6.0 to >= 0.6.1, < 0.7.0
* Update repo-config from v0.11.0 to v0.13.0

## New Features

* Add the Public Order Book extension to the client
    * Add the `PublicOrder` and `PublicOrderFilter` types
    * Add the `receive_public_order()` endpoint

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
