# Frequenz Electricity Trading API Client

[![Build Status](https://github.com/frequenz-floss/frequenz-client-electricity-trading-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-client-electricity-trading-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-client-electricity-trading)](https://pypi.org/project/frequenz-client-electricity-trading/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-client-electricity-trading-python/)

## Introduction

Electricity Trading API client for Python
The Frequenz Electricity Trading API client for Python is an easy-to-use Python interface built to interact with the Frequenz Electricity Trading API. It allows you to create orders, get market data, and manage your orders.

## Features

* **Create and manage gridpool orders**: Place new orders, update existing ones, and cancel orders when necessary.
* **Stream live data**: Get real-time updates on market data, including order books, trades, and market prices.
* **Retrieve historical data**: Access historical data on market trades.

## Supported Platforms

The following platforms are officially supported (tested):

* **Python:** 3.11
* **Operating System:** Ubuntu Linux 20.04
* **Architectures:** amd64, arm64

## Usage

### Installation

We assume you are on a system with Python available. If that is not the case,
please [download and install Python](https://www.python.org/downloads/) first.


To install the Frequenz Electricity Trading AP, you probably want to create a new virtual
environment first. For example, if you use a `sh` compatible shell, you can do this:

```sh
python3 -m venv .venv
. .venv/bin/activate
```

Then, just install using `pip`. Replace `VERSION` with the specific version you wish to install:

```sh
# Choose the version you want to install
VERSION=0.2.3
pip install frequenz-client-electricity-trading==$VERSION
```


## Documentation

For more information, please visit the [documentation
website](https://frequenz-floss.github.io/frequenz-client-electricity-trading/).


## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
