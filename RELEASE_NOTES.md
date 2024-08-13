# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- Refactor order states following `frequenz-api-electricity-trading` update to <branch>:

  - Remove obsolete order states CANCEL_REQUESTED and CANCEL_REJECTED

- The minimum required version of `frequenz-client-base` is now 0.3

- The minimum required version of `frequenz-channels` is now 1.0

## New Features

- Restrict the decimal points of the quantity and price values

- Integrate the BaseApiClient v0.5 into the client

- Add key based authorization to the client

## Bug Fixes

- Handle missing protobuf fields in Filter classes
