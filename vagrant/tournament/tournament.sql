-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\c tournament;

DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players (
	id			serial		primary key,
	name		text,
	matches		integer,
	wins		integer
);

DROP TABLE IF EXISTS matches CASCADE; 
CREATE TABLE matches (
	id			serial		primary key,
	player1		integer		references		players(id),
	player2		integer		references		players(id)
);

DROP TABLE IF EXISTS scores CASCADE;
CREATE TABLE scores (
	match		integer		references		matches(id),
	winner		integer		references		players(id),
	loser 		integer		references		players(id)
);