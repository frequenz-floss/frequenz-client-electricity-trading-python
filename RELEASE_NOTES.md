# Frequenz Electricity Trading API Client Release Notes

## Summary

<!-- Here goes a general summary of what this release is about -->

## Upgrading

- `DeliveryPeriod` instances now require a `DeliveryDuration` as an argument in their constructors, and can't be instantiated from `timedelta`s any more.  Instead, `DeliveryDuration`s can be created from `timedelta` instances with `DeliveryDuration.from_timedelta()`.

- Timestamps are no-longer automatically converted to UTC.  If provided timestamps are not in UTC, the client will raise an exception.

## New Features

<!-- Here goes the main new features and examples or instructions on how to use them -->

## Bug Fixes

<!-- Here goes notable bug fixes that are worth a special mention or explanation -->
