#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    # open session
    cxn = connect()
    cur = cxn.cursor()
    
    # renive all matches from table
    cur.execute ('DELETE FROM scores')
    cur.execute ('DELETE FROM matches WHERE id > -1')

    # store changes and close session
    cxn.commit()
    cxn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    # open session
    cxn = connect()
    cur = cxn.cursor()

    # remove all players from table
    cur.execute ('DELETE FROM players WHERE id > -1')
    
    # store changes and close session
    cxn.commit()
    cxn.close()  

def countPlayers():
    """Returns the number of players currently registered."""
    # open session
    cxn = connect()
    cur = cxn.cursor()

    # count the number of rows in players relation
    cur.execute('SELECT COUNT(id) FROM players;')
    # since count returns tuple, store the first integer in tuple
    (num_players,) = cur.fetchone()
    
    # close session and return
    cxn.close()
    return num_players

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    # open session
    cxn = connect()
    cur = cxn.cursor()
    
    # add player to players relation
    # note the tuple syntax for parametrized strings
    # and the expectation that the name is enclosed in double quotes
    cur.execute('INSERT INTO players (name, matches, wins) VALUES (%s,%s,%s)', (name,0,0,))

    # close session
    cxn.commit()
    cxn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    # open session
    cxn = connect()
    cur = cxn.cursor()

    # query for per-player matches played and number of wins
    cur.execute('SELECT id, name, wins, matches FROM players ORDER BY wins DESC;')

    # store list of player standings
    standings = cur.fetchall()

    # close session and return values
    cxn.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # open session
    cxn = connect()
    cur = cxn.cursor()

    # add winner and loser ids for match
    cur.execute('INSERT INTO scores (winner, loser) VALUES (%s, %s)' , (winner, loser,))
    # increment the winner's wins and matches played
    cur.execute('UPDATE players SET matches = matches + 1, wins = wins + 1 WHERE id = %s', (winner,))
    # increment the loser's matches played
    cur.execute('UPDATE players SET matches = matches + 1 WHERE id = %s', (loser,))
    
    # update database and close session
    cxn.commit()
    cxn.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # open session
    cxn = connect()
    cur = cxn.cursor()

    # get players sorted by score
    cur.execute('SELECT id, name FROM players ORDER BY wins DESC')
    result = cur.fetchall()

    # empty list for organizing upcoming round
    this_round = []

    # loop through query results and store evenly matched pairs
    i = 0
    while i < len(result):
        # pair each player with player on next row
        this_pair = (result[i][0], result[i][1], result[i+1][0], result[i+1][1])
        this_round.append(this_pair)
        # skip rows for next pairing
        i += 2
    
    # update database and close session
    cxn.commit()
    cxn.close()
    return (this_round)
