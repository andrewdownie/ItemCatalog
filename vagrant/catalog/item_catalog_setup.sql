--
-- PostgreSQL database dump
--


CREATE TABLE category(
    name text,
    id integer NOT NULL
);


CREATE TABLE items(
    name text,
    category_id integer,
    description text,
    date_created date,
    id integer NOT NULL
);


CREATE TABLE users(
    username text,
    id integer NOT NULL
);

