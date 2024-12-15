## To run 4chan_cralwer
  1. Created a virtual environment `dev`. Please go into this venv to run this project.
  Activate your new environment: `source env/dev/bin/activate`

  2. pip installed all the necesary requirements.

  3. Downloaded the docker image for postgres(timescaledb) and faktory as per the commands given in the README.
  
  * The `docker run` command creates a new container from the specified image. Hence I created and named the postgres container as `timescaledb-reddit` and named faktory model container as `faktory-reddit`(as shown in the readme file).
  
  * Now as the docker containers are created, just user `sudo docker start <container_name>` or `sudo docker stop <container_name>` to start and stopn the containers. No need to make the "docker run" command again.
      ```
      sudo docker start faktory-reddit

      sudo docker start timescaledb-reddit
      ```

  4. Created a `reddit_data` DATABASE in postgres(timescaledb). Created a table `posts` and `comments` under the database `reddit_data`.
  To access a psql shell: `docker exec -it timescaledb-reddit psql -U postgres`

  5. Created .env file and added the neccessary env values (FAKTORY_SERVER_URL and DATABASE_URL)

  6. To run the application, run `python3 reddit_crawler.py`

  Note, to run most of the command, you need to prepend "sudo" to the command, else the permission is denied. 