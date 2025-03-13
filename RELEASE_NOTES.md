# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

* Updated frequenz-client-common version range to >=0.1.0, <0.4.0
* Upgraded grpcio to >=1.68.1, <2 and protobuf to >=5.29.2, <6 to resolve compatibility issues 
* Unify Public Trades streaming and listing (to align with the proto changes in v0.5.0)
    * Removed `list_public_trades`
    * Replaced `public_trades_stream` with `receive_public_trades`
    * `receive_public_trades` now supports an optional time range (`start_time`, `end_time`)

## New Features


## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
