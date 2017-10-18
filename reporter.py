"""This reporter.py file holds the Python code that analyzes the news
database, using SQL style querying and outputs a plain text file containing
the answers to the following three questions:
1) What are the most popular three articles of all time?
2) Who are the most popular article authors of all time?
3) On which days did more than one percent of requests lead to errors?.

NOTE: The creation and population of views and tables needs to only run once!
If you run this code more than once you need to comment out all calls to
functions that create tables or views in the if __name__ = __main__ block.
There is a block of hashtags that signal where you should comment at the end
of this file. 
"""

import re
import psycopg2

def articles_and_authors():
	"""This function creates a view that called articles_and_authors by 
	joining the articles and authors tables on the articles.author column and
	the authors.id column. This view will be useful in finding the top three
	authors.
	"""
	cursor.execute("""create view articles_and_authors as select
		articles.author, articles.title, articles.slug, articles.time,
		articles.id, authors.name, authors.bio, authors.id as author_id from
		articles, authors where articles.author = authors.id""")
	db_conn.commit()

def update_log():
	"""This function creates and populates a table called updated_log to
	include most of the information from the log table excluding the ip column
	and including an additional column called article_slug that holds the slug
	of the article the path in log leads to. This is in preparation to answer
	question one.
	""" 
	cursor.execute("""create table updated_log as select path, method, status,
		time, id from log""")
	db_conn.commit()
	cursor.execute("alter table updated_log add article_slug text")
	db_conn.commit()
	cursor.execute("select path from updated_log")
	paths = cursor.fetchall()
	for p in paths:
		pattern = re.compile('article/(.*)')
		searched = pattern.search(p[0])
		if searched == None:
			cursor.execute("""update updated_log set article_slug = {} where
				updated_log.path = '{}'""".format('NULL', p[0]))
			db_conn.commit()
		else:
			a_slug = searched.group(1)
			cursor.execute("""update updated_log set article_slug = '{}' where
				updated_log.path = '{}'""".format(a_slug, p[0]))
			db_conn.commit()

def articles_and_logs():
	"""This function creates a view called articles_and_logs that combines the
	articles table with the newly created updated_log table. It joins both
	tables through the articles' slug column and the updated_log's
	article_slug column. This view is useful in solving question one.
	"""
	cursor.execute("""create view articles_and_logs as select articles.author,
		articles.title, articles.slug, articles.time, articles.id,
		updated_log.method, updated_log.status, updated_log.article_slug,
		updated_log.time as log_time, updated_log.id as log_id from articles,
		updated_log where articles.slug = updated_log.article_slug""")
	db_conn.commit()


def top_three_articles():
	"""This function finds the top three most popular articles of all time
	using the view called articles_and_logs."""
	cursor.execute("""select articles_and_logs.id, articles_and_logs.title,
		count(articles_and_logs.method) as num_views from articles_and_logs
		where articles_and_logs.method = 'GET' group by 
		articles_and_logs.title, articles_and_logs.id order by num_views desc
		limit 3""")
	db_conn.commit()
	return cursor.fetchall()

def top_three_authors():
	"""This function uses the articles_and_authors view and the 
	articles_and_logs view to find the top three most popular authors of all
	time ie. the top three most viewed articles."""
	cursor.execute("""select articles_and_authors.name,
		count(articles_and_logs.method) as num_views from articles_and_logs, 
		articles_and_authors where articles_and_authors.title = 
		articles_and_logs.title and articles_and_logs.method = 'GET' group by 
		articles_and_authors.name order by num_views desc limit 3""")
	db_conn.commit()
	return cursor.fetchall()

def requests_per_day():
	"""This function creates a table called requests_per_day with columns
	called date and total_requests. This is in preparation to answer question
	three.
	"""
	cursor.execute("""create table requests_per_day as select date(time),
		count(*) as total_requests from log group by date(time)""")
	db_conn.commit()
	
def error_requests_per_day():
	"""This function creates a table called error_requests_per_day with 
	columns called e_date and num_errors. This is in preparation to answer
	question three.
	"""
	cursor.execute("""create table error_requests_per_day as select date(time)
		as e_date, count(*) as num_errors from log where status =
		'404 NOT FOUND' group by e_date""")
	db_conn.commit()

def total_and_errors():
	"""
	This function creates a table called total_and_errors by joining the
	requests_per_day table and the error_requests_per_day table on the
	requests_per_day.date column and the error_requests_per_day.e_date column.
	"""
	cursor.execute("""create table total_and_errors as select * from
		requests_per_day join error_requests_per_day on requests_per_day.date
		= error_requests_per_day.e_date""" )
	db_conn.commit()

def days_with_too_many_errors():
	"""This function finds the days in which more than one percent of its
	requests resulted in an error and what the respective percentage was.
	"""
	cursor.execute("""select date, (cast(errors as float)/cast(total_requests
		as float)) from total_and_errors where (cast(errors as float)/
		cast(total_requests as float)) > 0.01""")
	db_conn.commit()
	return cursor.fetchall()

if __name__ == '__main__':
	db_conn = psycopg2.connect(database='news')
	cursor = db_conn.cursor()

	##########################################################################
	#  The lines sandwiched between the hashtag lines must be run the first  #
	#  time you run this code, any time after that you will have to comment  #
	#  them out.                                                             #
	##########################################################################   
	articles_and_authors()
	update_log()
	articles_and_logs()
	requests_per_day()
	error_requests_per_day()
	total_and_errors()
	##########################################################################

	top_3_articles = top_three_articles()
	print """This is a list of the top three articles and their respective
	number of views: """ + str(top_3_articles)
	top_3_authors = top_three_authors()
	print """This lists the top three authors and their respective total views
	over all of their articles: """ + str(top_3_articles)
	bad_days = days_with_too_many_errors()
	print """This lists pairs of days with more than one percent of requests
	resulting in error and their respective proportions: 
	""" + str(top_3_articles)

	db_conn.close()
