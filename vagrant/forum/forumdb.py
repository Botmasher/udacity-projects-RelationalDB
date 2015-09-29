#
# Database access functions for the web forum.
# 
import psycopg2

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      Results from the table that match the query formatted as a dict
    '''
    db = psycopg2.connect('dbname=forum')
    cursor = db.cursor()
    cursor.execute('select time, content from posts order by time desc')
    # reformat as dictionary rather than just fetchall
    posts = ( {'content': str(row[1]), 'time': str(row[0])} for row in cursor.fetchall() )
    db.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    db = psycopg2.connect("dbname=forum")
    cursor = db.cursor()
    cursor.execute("insert into posts (content) values ('%s')" % (content,) )
    db.commit()
    db.close()
