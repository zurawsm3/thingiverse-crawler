# Thingiverse.com crawler
Program crawl whole data from thingiverse.com

## Table of contents
* [General info](#general-info)
* [Setup](#setup)
* [Technologies](#technologies)

## General info
Whole data is saved in postgreSQL volume. Moreover every html page of website is stored in html directory.

## Setup
In */thingiverse_pro/last_nb/num_thing.txt* user should add the latest id of thing in Thingiverse. Crawler start scrapy from the latest one to the oldest one.
> docker volume create thingiverse_database <br />
> docker-compose up

## Technologies
 * Scrapy
 * Docker-compose
 * PostgreSQL
 * Psycopg2
