# Economic Research - FRED API

## Setup

1. `git clone https://dansheikh/fred.git $HOME/Downloads` 

2. Create configuration file with the following key-value pairs:

<code>
{
    "protocol": "https",
    "host": "api.stlouisfed.org",
    "endpoints": { "observations": "/fred/series/observations" },
    "api_key": "...",
    "series": ["GDPC1", "UMCSENT", "UNRATE"],
    "file_type": "json"
}
</code>

2. `git clone https://github.com/dansheikh/docks.git`

3. Within the "Sandbox" directory of the "docks" clone execute: `docker build -t fred -f ubuntu/Dockerfile .`

4. Start container (in daemon mode) with: `docker run --rm -t -d -P -p 5432:5432 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/Downloads/fred:/home/dev/Projects/fred fred`

5. Connect to running container with: `docker exec -u dev -it [container id] env TERM=xterm /bin/bash -l`

6. Create database structure with: `PGPASSWORD=postgres psql -U postgres -a -q -f /home/dev/Projects/fred/resources/fred.sql`

7. Launch ETL application with: `/home/dev/Projects/fred/app.py [options] /home/dev/Projects/fred/config.json`

## SQL Example
### Average unemployment between 1980 and 2015
<code>
select date_trunc('year', date_stamp), avg(val_sum) from (select date(date_stamp) date_stamp, sum(value) val_sum from economics.unrate where date_stamp between '19791231' and '20151231'  group by 1) subq group by 1 order by 1 desc;
</code>