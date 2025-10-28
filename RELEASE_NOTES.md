# Frequenz Electricity Trading API Client Release Notes

## Summary

This release adds enhanced filtering capabilities for gridpool orders and trades, with support for tag-based filtering and more flexible time-based queries.

## New Features

* **Tag filtering for gridpool trades**: The `gridpool_trades()` method now accepts a `tag` parameter to filter trades by tag. The `GridpoolTradeFilter` dataclass has been updated accordingly.

* **Flexible time filtering with `DeliveryTimeFilter`**: Replaced the restrictive `delivery_period` parameter with a more flexible `delivery_time_filter` across gridpool orders and trades methods. The new `DeliveryTimeFilter` supports:
  - Time interval filtering with optional start/end times
  - Multiple delivery duration filters
  - More granular control over time-based queries

* **New types for time filtering**: Added `Interval` and `DeliveryTimeFilter` types to support the enhanced filtering API.

* Support tags in CLI create-order command.

## Breaking Changes

* The `delivery_period` parameter has been replaced with `delivery_time_filter` in the following methods:
  - `list_gridpool_orders()`
  - `stream_gridpool_orders()`
  - `gridpool_trades()`

  Note: The `create_gridpool_order()` method maintains backward compatibility by keeping both parameters.

* Updated API imports from v1 to v1alpha8 for common types.
