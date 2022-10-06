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

### How to handle migrations

Changes to the data model need to be handled through migrations. We use aerich to manage the migration files. 
Both our CLI and our web service are configured in such a way that migrations are run transparently when the package is
updated. If you want to test that the update doesn't corrupt your data, we suggest trying the update in a test database.

To create a new migration file, use aerich CLI. It will take care of generating the file. If further code is necessary,
add it to the new migration file.

Since we support two database (sqlite and postgres) that have slightly different dialects and since aerich doesn't 
really support this scenario, it is necessary to generate migrations separately and place the migrations files in the 
respective folders.

Aerich picks up the migrations according to the scheme of the db in the configuration.

Currently the consistency of the migrations for the different databases is not tested so please pay extra care when 
committing a change and request special review.
