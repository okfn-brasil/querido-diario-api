# querido-diario-api

Welcome to the Querido Diário API project! The goal of this repository is keep
the source code used to build the API used to make available the gazettes crawled
by the [Querido Diário](https://github.com/okfn-brasil/querido-diario) project. 

## Requisites

The whole project is build and run inside containers and is supported only in 
Linux environments (for now). As we run everything inside containers you just need
to install [`podman`](https://podman.io/) to run locally in your machine. If 
you are not familiarize with `podman`, you can think it as a lightweight 
`docker`/`docker-compose`. It exists in almost all Linux distributions packages 
repositories. 

Please, check podman [documentation](https://podman.io/getting-started/installation.html) 
to see how to installed it in your environments. If you face some difficulties 
with podman, let us know!

## Build

In order to be able to run and test your changes in the project, first, you need
to build the container image used during development. For that you can use the
following command:

```
make build
```

After that you will have a container image which can be use to run the API 
locally during development.

## Running

To run the API locally in your machine, you can run the following command:

```
make run
```

This command will start all containers necessary to run the API. In other words,
it starts the database and the API container. If everything goes fine, you 
should be able to query the API at `localhost:8080/gazettes/<City IBGE Code>`

NOTE: When you want to restart the API, just quit the API process and 
execute `make rerun` again. You do not need to restart the database.

You can all check the interactive documentation at `localhost:8080/docs`. Using 
the docs page, you can all send request to the API. But to see it working you
need to insert data into the database. There is another make target, `make apisql`,
which open the `psql` and connect to the database. Thus, you can insert data
using some `INSERT INTO ...` statements and test the API. ;)


### Using suggestion endpoint

You need to create a token at [Mailjet](www.mailjet.com) to run
application and send email (put on `config/current.env`).

## Tests

The project uses TDD during development. This means that there are no changes 
without tests. We should always seek 100% source code coverage. Another way to
think about tests is the following:

>  "Write the test which forces you to write the code which you already know that you wanna write."
> By Robert C. Martin (a.k.a. Uncle Bob)

To run the tests you can do the following:

```bash
make test
```

NOTE: You do not need to restart the test database all the times you want to
run the tests. Once the database is running, you need to run the `make retest` 
again.

You should do that just the first time you run the tests. After that, you can just
run `make retest`. Of course, if you remove the database with `make destroydatabse`
or reboot the machine, you need to start the database again.

If you can to see the code coverage:

```bash
make coverage
```
