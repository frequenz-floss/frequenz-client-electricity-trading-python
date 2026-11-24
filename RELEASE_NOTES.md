# Frequenz Electricity Trading API Client Release Notes

## Summary

This release adds support for `frequenz-channels` v2.0.0, while still supporting v1 (`frequenz-channels >= 1.6.1, < 3`).

## New Features

* `trading-cli` falls back to `FREQUENZ_API_KEY` and `FREQUENZ_API_SECRET` when neither `--auth_key` nor `--sign_secret` is given, so `--auth_key` is no longer required.
