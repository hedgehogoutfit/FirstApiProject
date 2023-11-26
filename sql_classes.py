from datetime import datetime
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import List, Tuple
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASS')

con_pool = SimpleConnectionPool(minconn=1, maxconn=10,
                                host="localhost",
                                port="5432",
                                database="postgres",
                                user=db_user,
                                password=db_password)


@contextmanager
def connect():
    connection = con_pool.getconn()
    cursor = connection.cursor()
    try:
        yield connection, cursor
    finally:
        cursor.close()
        con_pool.putconn(connection)




def get_datetime():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    return date_str


def add_articles_database(articles: List[tuple]):
    with connect() as (con, cur):
        cur.execute(generate_query(articles), articles)
        ides = cur.fetchall()
        con.commit()
        ids = [id[0] for id in ides]

    return ids





def generate_query(articles: List[tuple]):
    length = len(articles) // 3
    ss = ["(%s, %s, %s)" for x in range(length)]
    jj = ", ".join(ss)

    query = f"""INSERT INTO
    article(title, content, author)
    VALUES{jj} returning id;"""

    return query


class EditArticle:
    def __init__(self, id):
        self.id = id

    def check_if_exists(self):
        with connect() as (con, cur):
            cur.execute("""select id from article
                              where id = %s;""", (self.id,))
            result = cur.fetchone()
        if not result:
            raise Exception("id doesn't exist")

    def delete_article(self):
        with connect() as (con, cur):
            cur.execute("""delete from article where id = %s;""", (self.id,))
            con.commit()
        with connect() as (con, cur):
            cur.execute("""delete from comments where article_id = %s;""", (self.id,))
            con.commit()

    def edit_content(self, new_content):
        with connect() as (con, cur):
            cur.execute("""update article set content = %s where id = %s;""", (new_content, self.id))
            con.commit()

    def edit_author(self, new_author):
        with connect() as (con, cur):
            cur.execute("""update article set author = %s where id = %s;""", (new_author, self.id))
            con.commit()

    def edit_title(self, new_title):
        with connect() as (con, cur):
            cur.execute("""update article set title = %s where id = %s;""", (new_title, self.id))
            con.commit()

    def add_comment(self, content, author):
        date = get_datetime()
        with connect() as (con, cur):
            cur.execute("""insert into comments (content, author, date, article_id) values (%s, %s, %s, %s);""",
                        (content, author, date, self.id))
            con.commit()

    def delete_comment(self, comment_id):
        pass

    def add_like(self):
        with connect() as (con, cur):
            cur.execute("""update article set:""", (self.id,))


"""-----------------------------get posts with comments by parameters-------------------------"""


def get_posts(ids):
    """change to list of ids"""
    with connect() as (con, cur):
        cur.execute("""select title, author, content, likes, date
              from Article
              where id = %s;""", (id,))
        articles = cur.fetchall()
    return articles


def get_comments(article_id):
    with connect() as (con, cur):
        cur.execute("""select id, author, content,  date
              from comments
              where article_id = %s;""", (id,))
        comments = cur.fetchall()
    return comments


def get_latest_articles(n: int) -> list[(), ()]:
    with connect() as (con, cur):
        cur.execute("""select id, title, author, content, likes, date
        from Article
        order by date desc
        limit %s;""", (n,))
        result = cur.fetchall()
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

def article_to_dict(article):
    date_obj = article[5]
    date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    d = {'post_id': article[0],
         'title': article[1],
         'author': article[2],
         'content': article[3],
         'likes': article[4],
         'date': date}
    return d


def comments_to_dict(comments):
    comment_list = []
    for comment in comments:
        date_obj = comment[3]
        date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        l = {'comment_id': comment[0],
             'author': comment[1],
             'content': comment[2],
             'date': date}
        comment_list.append(l)
    return comment_list


def posts_plus_comments(posts):
    new_result = []
    for post in posts:
        post_dict = article_to_dict(post)
        post_id = post_dict.get('id')
        comments = get_comments(post_id)
        comments_list = comments_to_dict(comments)
        post_dict['comments'] = comments_list
        new_result.append(post_dict)
    return new_result


def get_top_by_likes(n):
    with connect() as (con, cur):
        cur.execute("""select id, title, author, content, likes, date
        from Article
        order by likes desc
        limit %s;""", (n,))
        result = cur.fetchall()
    return result


def get_articles_by_author(author):
    with connect() as (con, cur):
        cur.execute("""select id, title, author, content, likes, date
           from Article
           where author = %s;""", (author,))
        result = cur.fetchall()
    return result


if __name__ == '__main__':
    pass
