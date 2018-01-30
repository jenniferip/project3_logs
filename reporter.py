#!/usr/bin/env python

"""This reporter.py file holds the Python code that analyzes the news
database, using SQL style querying and outputs a plain text file containing
the answers to the following three questions:
1) What are the most popular three articles of all time?
2) Who are the most popular article authors of all time?
3) On which days did more than one percent of requests lead to errors?.
"""


import psycopg2


def articles_and_authors():
    """This function creates a view called articles_and_authors by selecting
    the authors' name column and articles' title and slug column after joining
    the articles and authors tables on the articles' author column and the
    authors' id column. This view will be useful in finding the top three
    articles and authors once it is combined with the log table.
    """
    cursor.execute("""CREATE OR REPLACE VIEW articles_and_authors AS SELECT
        authors.name, articles.title, articles.slug FROM authors, articles
        WHERE articles.author = authors.id""")
    db_conn.commit()


def article_author_log():
    """This function creates a view called article_author_log by combining the
    articles_and_authors view, made in the function above, with the log table
    on the articles_and_authors' slug column and the log's path column which
    contains the slug of the article it leads to. This view has all of the
    columns from the articles_and_authors view as well as all of the columns
    from the log table. This will be useful in finding the top three articles
    and authors.
    """
    cursor.execute("""CREATE OR REPLACE VIEW article_author_log AS SELECT *
        FROM articles_and_authors LEFT JOIN log ON log.path = '/article/' || 
        articles_and_authors.slug""")
    db_conn.commit()


def top_three_articles():
    """This function finds the top three most popular articles of all time
    using the view called article_author_log.
    """
    cursor.execute("""SELECT title, count(method) AS num_views FROM
        article_author_log WHERE status = '200 OK' GROUP BY title ORDER BY
        num_views DESC LIMIT 3""")
    return cursor.fetchall()


def top_three_authors():
    """This function uses the article_author_log view to find the top three
    most popular authors of all time ie. the top three most viewed authors
    over all of their articles.
    """
    cursor.execute("""SELECT name, count(method) AS num_views FROM
        article_author_log WHERE status = '200 OK' GROUP BY name ORDER BY
        num_views DESC""")
    return cursor.fetchall()


def requests_per_day():
    """This function creates a view called requests_per_day with columns
    called date and total_requests. This is in preparation to answer question
    three.
    """
    cursor.execute("""CREATE OR REPLACE VIEW requests_per_day AS SELECT
        date(time), count(*) AS total_requests FROM log GROUP BY
        date(time)""")
    db_conn.commit()


def error_requests_per_day():
    """This function creates a view called error_requests_per_day with
    columns called e_date and num_errors. This is in preparation to answer
    question three.
    """
    cursor.execute("""CREATE OR REPLACE VIEW error_requests_per_day AS SELECT
        date(time) AS e_date, count(*) AS num_errors FROM log WHERE status =
        '404 NOT FOUND' GROUP BY e_date""")
    db_conn.commit()


def total_and_errors():
    """This function creates a view called total_and_errors by joining the
    requests_per_day table and the error_requests_per_day table on the
    requests_per_day.date column and the error_requests_per_day.e_date column.
    """
    cursor.execute("""CREATE OR REPLACE VIEW total_and_errors AS SELECT * FROM
        requests_per_day JOIN error_requests_per_day ON requests_per_day.date
        = error_requests_per_day.e_date""")
    db_conn.commit()


def days_with_too_many_errors():
    """This function finds the days in which more than one percent of its
    requests resulted in an error and what the respective percentage was.
    """
    cursor.execute("""SELECT date,
        (cast(num_errors as float)/cast(total_requests as float)) FROM
        total_and_errors WHERE
        (cast(num_errors as float)/cast(total_requests as float)) > 0.01""")
    return cursor.fetchall()


if __name__ == '__main__':
    db_conn = psycopg2.connect(database='news')
    cursor = db_conn.cursor()

    articles_and_authors()
    article_author_log()
    requests_per_day()
    error_requests_per_day()
    total_and_errors()

    top_3_articles = top_three_articles()
    top_3_authors = top_three_authors()
    bad_days = days_with_too_many_errors()

    db_conn.close()

    results_file = open('reporter_results.txt', 'w')

    results_file.write("""These are the top three articles in our """ +
                       """database with their respective number of views.
                       \n""")
    for article in top_3_articles:
        results_file.write(str(article[0]) + ' - ' + str(article[1]) +
                           ' views ' + '\n')
    results_file.write('\n')

    results_file.write("""Next, are the top three authors in our """ +
                       """database with their respective total views """ +
                       """over all articles they have written.\n""")
    for author in top_3_authors:
        results_file.write(str(author[0]) + ' - ' + str(author[1]) +
                           ' views ' + '\n')
    results_file.write('\n')

    results_file.write("""Finally, these are the days in which more than """ +
                       """one percent of its requests resulted in an """ +
                       """errorthe percent of errors.\n""")
    for day in bad_days:
        results_file.write(str(day[0]) + ' - ' + str(day[1]*100) + '%' + '\n')

    results_file.close()
