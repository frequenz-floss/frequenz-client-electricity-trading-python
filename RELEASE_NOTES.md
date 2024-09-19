# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

<!-- Here goes notes on how to upgrade from previous versions, including deprecations and what they should be replaced with -->

## New Features

- Add input validation checks for `price`, `quantity`, `delivery_period`, `valid_until`, `execution_option` and `order_type`.
- Add unit tests for requests with invalid input parameters.
- Updated dependencies to latest versions

## Bug Fixes

- Fix variable name `max_nr_orders` to `max_nr_trades` for trades requests
