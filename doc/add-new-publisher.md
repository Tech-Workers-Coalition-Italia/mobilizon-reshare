# Add a new publisher
To add a new publishing platform to Mobilizon Reshare you need to follow these steps.

## Add an example configuration in `mobilizon_reshare/.secrets.toml`
## Add suitable validators to `mobilizon_reshare/config/notifiers.py` and `mobilizon_reshare/config/publishers.py`
## Create a new file inside `mobilizon_reshare/publishers/platforms`
## Add suitable mappings inside `mobilizon_reshare/publishers/platform_mapping.py`
## Create suitable message templates inside `mobilizon_reshare/publishers/templates`
## Add some unit test inside `tests/publishers`