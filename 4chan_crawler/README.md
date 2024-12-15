# 4chan crawler

This repository is from live coding sessions from Binghamton University's 2024 CS 415/515 class.

## Postgres (Timescale db) install with docker

To install start up.

```
docker pull timescale/timescaledb-ha:pg16
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=testpassword timescale/timescaledb-ha:pg16
```

To access a psql shell:

`docker exec -it timescaledb psql -U postgres`

## sqlx migrations
if following the above, then you can use this as database url `DATABASE_URL=postgres://postgres:testpassword@localhost:5432/chan_crawler`

`sql database create`

`sql database drop`

`sqlx migrate add -r --source /path/you/want/migrations "some descriptive name"`

`sqlx migrate run`

`sqlx migrate revert`

## Faktory

Install from docker: `docker pull contribsys/faktory`

Run:

```
docker run -it --name faktory \
  -v ~/projects/docker-disks/faktory-data:/var/lib/faktory/db \
  -e "FAKTORY_PASSWORD=password" \
  -p 127.0.0.1:7419:7419 \
  -p 127.0.0.1:7420:7420 \
  contribsys/faktory:latest \
  /faktory -b :7419 -w :7420
  ```

  ## Python virtual environment

  You probably want to use virtual environments to keep evertying clean.

  `python -m venv ./env/dev`

  Activate your new environment: `source env/dev/bin/activate`

  Deactivate your environment: `deactivate`

  




