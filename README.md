# Logs Project

`/project3_logs` is a folder containing the files used to create a reporting tool on the news database which holds information about newspaper articles, authors, and logs that display the requests that where made to the database and the outcome of those requests. 

The file `reporter.py` holds all of the Python code for the reporter tool which answers the following three questions and writes the results into a text file called `reporter_results.txt`.

1. What are the most popular three articles of all time?
2. Who are the most popular article authors of all time?
3. On which days did more than one percent of requests lead to errors?

### How to run

To run the reporter tool, you must download this folder and move it into your local directory containing the virtual machine that holds the shared data from the news database; this should be a directory called `/vagrant`. Once you have moved the `/project3_logs` folder into the vagrant directory, you will need to start up the virtual machine from within the vagrant directory by running `vagrant up` and then `vagrant ssh`. If that works succesfully, you will then enter the `/project3_logs` folder from the virtual machine and run `python reporter.py`.

__NOTE:__ Running this code will create new views of specific names, if a view with the same name already exists the code will replace it!     

### Files

The files included are: 
* `reporter.py` - This file contains all Python code that acts on the news database for the reporter tool. It defines various methods that create tables or views or execute queries over the database to get the answers to the above questions.
* `README.md` 

__NOTE:__ You may need the `newsdata.sql` file containing all data in this project folder. I could not include it here as it is too large to share and store.

### Describing the Extra Views and Tables Created

Below is a list of the extra views `reporter.py` creates in order to more easily find the answers to our questions. There are also descriptions of each view and a little bit about how and why they were created. Also, all tables and views are created within a function of the same name.
* __articles_and_authors *(view)*__ - This view is useful in answering questions one and two, specifically it will be combined with the log table to create the article_author_log view that ultimately gives us the answers we want. It has the columns: name from the authors table and the columns title and slug from the articles table. Create it by running the following query:
    ```
    create or replace view articles_and_authors
    as select authors.name, articles.title, articles.slug 
    from authors, articles
    where articles.author = authors.id
    ```
* __article_author_log *(view)*__ - The query below creates this view. This view has all of the columns from the articles_and_authors view as well as all of the columns from the log table. It is necessary for answering questions one and two with this reporter tool.
    ```
    create or replace view article_author_log
    as select * 
    from articles_and_authors left join log 
    on log.path like %||articles_and_authors.slug||%
    ```
* __requests_per_day *(view)*__ - This view is one of two preparatory views used in creating the ultimate total_and_errors view described below which is necessary for answering the third and final question. Create this view with the following query:
    ```
    create or replace view requests_per_day
    as select date(time), count(*) as total_requests 
    from log group by date(time)
    ```
* __error_requests_per_day *(view)*__ - This view is the second of two preparatory views used in creating the ultimate total_and_errors view described below which is necessary for answering the third and final question. Create this view with the following query:
    ```
    create or replace view error_requests_per_day 
    as select date(time) as e_date, count(*) as num_errors 
    from log 
    where status = '404 NOT FOUND' group by e_date
    ```
* __total_and_errors *(view)*__ - This is the final view necessary for answering the third and final question, create it using the following query:
    ```
    create or replace view total_and_errors
    as select *
    from requests_per_day join error_requests_per_day 
    on requests_per_day.date = error_requests_per_day.e_date
    ```
