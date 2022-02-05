# Contributing
## Develop

To run pre-commit hooks run `pre-commit install` after cloning the repository.

Make sure to have `pre-commit` installed in your active python environment. To install: `pip install pre-commit`. For more info: https://pre-commit.com/.

To install dependencies you can either use [Guix](https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare/blob/master/doc/development-environment-with-guix.md) or poetry:

```shell
$ poetry install
Installing dependencies from lock file

Package operations: 44 installs, 0 updates, 0 removals

[...]

Installing the current project: mobilizon-reshare (0.1.0)
$
```

### Testing

To run the test suite, run `scripts/run_pipeline_tests.sh` from the root of the repository.

At the moment no integration test is present and they are executed manually. Reach out to us if you want to
access the testing environment or you want to help automate the integration tests.
