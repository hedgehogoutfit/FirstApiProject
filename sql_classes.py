from typing import List, Dict
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from functools import  lru_cache


psql = """postgresql://postgres:123@localhost:5432/first"""

def connect() -> psycopg.connect:
    conn = psycopg.connect(
        dbname="first",
        user="postgres",
        password="123",
        host="localhost",
        port="5432",
        row_factory=dict_row
    )
    return conn

@lru_cache()
def get_pool() -> ConnectionPool:
    return ConnectionPool(conninfo=psql)

pool = get_pool()

def add_post(title, author, content):
    with connect() as con, con.cursor() as cur:
        id = cur.execute("""insert into posts (title, author, content) values (%s, %s, %s)
                        returning post_id""", (title, author, content)).fetchone()
        return id


class EditArticle:
    def __init__(self, id):
        self.id = id

    def check_if_exists(self):
        with connect() as con, con.cursor() as cur:
            result = cur.execute("""select post_id from posts
                              where post_id = %s;""", (self.id,)).fetchone()
        if not result:
            raise Exception("id doesn't exist")

    def delete_article(self):
        with connect() as con, con.cursor() as cur:
            cur.execute("""delete from posts where post_id = %s;""", (self.id,))

        with connect() as con, con.cursor() as cur:
            cur.execute("""delete from comments where post_id = %s;""", (self.id,))

    def edit_content(self, new_content):
        with connect() as con, con.cursor() as cur:
            cur.execute("""update posts set content = %s where post_id = %s;""", (new_content, self.id))

    def edit_author(self, new_author):
        with connect() as con, con.cursor() as cur:
            cur.execute("""update posts set author = %s where post_id = %s;""", (new_author, self.id))

    def edit_title(self, new_title):
        with connect() as con, con.cursor() as cur:
            cur.execute("""update posts set title = %s where post_id = %s;""", (new_title, self.id))

    def add_comment(self, content, author):
        with connect() as con, con.cursor() as cur:
            cur.execute("""insert into comments (content, author, post_id) values (%s, %s, %s);""",
                        (content, author, self.id))

    def delete_comment(self, comment_id):
        pass

    def add_like(self):
        with connect() as con, con.cursor() as cur:
            cur.execute("""update article set:""", (self.id,))


"""-----------------------------get posts with comments by parameters-------------------------"""


def get_posts(ides: List[int]) -> List[Dict]:
    with connect() as con, con.cursor() as cur:
        posts = cur.execute("""select title, author, content, likes, datetime
              from posts
              where post_id = any(%s);""", [ides]).fetchall()
    return posts

def get_posts2(ides: List[int]) -> List[Dict]:
    with pool.connection() as con, con.cursor() as cur:
        posts = cur.execute("""select title, author, content, likes, datetime
              from posts
              where post_id = any(%s);""", [ides]).fetchall()
    return posts


def get_comments(id: int) -> List[Dict]:
    with connect() as con, con.cursor() as cur:
        cur.execute("""select id, author, content,  date
              from comments
              where post_id = %s;""", (id,))
        comments = cur.fetchall()
    return comments


def get_latest_posts(n: int) -> list[Dict]:
    """return n latest posts"""
    with connect() as con, con.cursor() as cur:
        result = cur.execute("""select post_id, title, author, content, likes, datetime
        from posts
        order by datetime desc
        limit %s;""", (n,)).fetchall()
    return result


# class ArticleDTO:
#     def __init__(self, id, title, content, author, likes, date):
#         self.id = id
#         self.title = title
#         self.content = content
#         self.author = author
#         self.likes = likes
#         self.date = date.strftime("%Y-%m-%d %H:%M:%S")
#



def get_top_by_likes(n: int)-> List[Dict]:
    """return n posts with highest likes"""
    with connect() as con, con.cursor() as cur:
        result = cur.execute("""select id, title, author, content, date
        from Article
        order by likes desc
        limit %s;""", (n,)).fetchall()
    return result


def get_posts_by_author(author: str)-> List[Dict]:
    with connect() as con, con.cursor() as cur:
        result = cur.execute("""select post_id, title, author, content, datetime
           from posts
           where author = %s;""", (author,)).fetchall()
    return result


if __name__ == '__main__':
    # a = add_post('lal', 'kdfjl', 'dskj')
    a = get_posts2([1,2])
    print(a)

