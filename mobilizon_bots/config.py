from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="MOBOTS",
    settings_files=[
        "settings.toml",
        ".secrets.toml",
        "/etc/mobots.toml",
        "/etc/mobots_secrets.toml",
    ],
    validators=[
        # Ensure some parameters exists (are required)
        Validator("LOCAL_STATE_DIR", "LOG_DIR", "DB_PATH", must_exist=True),
        # Ensure some parameter mets a condition
        # conditions: (eq, ne, lt, gt, lte, gte, identity, is_type_of, is_in, is_not_in)
        Validator("LOCAL_STATE_DIR", "LOG_DIR", "DB_PATH", is_type_of=str),
        # check file or directory
        # validate a value is eq in specific env
        # Validator('PROJECT', eq='hello_world', env='production'),
        #
        # # Ensure some parameter (string) meets a condition
        # # conditions: (len_eq, len_ne, len_min, len_max, cont)
        # # Determines the minimum and maximum length for the value
        # Validator("NAME", len_min=3, len_max=125),
        #
        # # Signifies the presence of the value in a set, text or word
        # Validator("DEV_SERVERS", cont='localhost'),
        #
        # # Checks whether the length is the same as defined.
        # Validator("PORT", len_eq=4),
    ],
)

settings.validators.validate()
