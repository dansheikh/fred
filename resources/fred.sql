drop database if exists fred;
drop schema if exists economics cascade;
drop user if exists saintlouis;

create database fred;
create user saintlouis with password 'econ';

\connect fred;

create schema economics;

create table economics.gdpc1(
    id varchar(36) not null,
    realtime_start date not null,
    realtime_end date not null,
    date_stamp date not null,
    value float null, 
    primary key (id)
);

create table economics.umcsent(
    id varchar(36) not null,
    realtime_start date not null,
    realtime_end date not null,
    date_stamp date not null,
    value float null, 
    primary key (id)
);

create table economics.unrate(
    id varchar(36) not null,
    realtime_start date not null,
    realtime_end date not null,
    date_stamp date not null,
    value float null, 
    primary key (id)
);

grant all privileges on database fred to saintlouis;
grant all privileges on schema economics to saintlouis;
grant all privileges on all tables in schema economics to saintlouis;
