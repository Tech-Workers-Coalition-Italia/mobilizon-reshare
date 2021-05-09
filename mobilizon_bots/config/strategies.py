from dynaconf import Validator

next_event_validators = [
    Validator(
        "selection.strategy_options.break_between_events_in_minutes", must_exist=True
    )
]


strategy_name_to_validators = {"next_event": next_event_validators}


def get_validators(settings):
    return strategy_name_to_validators[settings["selection"]["strategy"]]
