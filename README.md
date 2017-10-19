# Logs Project

`/project3_logs` is a folder containing the files used to create a reporting tool on the news database which holds information about newspaper articles, authors, and logs that display the requests that where made to the database and the outcome of those requests. 

The file `reporter.py` holds all of the Python code for the reporter tool which answers the following three questions and writes the results into a text file called `reporter_results.txt`.

1. What are the most popular three articles of all time?
2. Who are the most popular article authors of all time?
3. On which days did more than one percent of requests lead to errors?

### How to run

To run the reporter tool, you must download this folder and move it into your local directory containing the virtual machine that holds the shared data from the news database; this should be a directory called `/vagrant`. Once you have moved the `/project3_logs` folder into the vagrant directory, you will need to start up the virtual machine from within the vagrant directory by running `vagrant up` and then `vagrant ssh`. If that works succesfully, you will then enter the `/project3_logs` folder from the virtual machine and run `python reporter.py`.

__NOTE:__ Running this code will create some tables and views in the database, which could result in an issue if a table or view already exists with the name of the table or view the code is attempting to create. If this occurs during the first run of the code, I suggest going into the function that creates the problematic table or view and change the name of the table or view it creates to something that will not overlap with the current state of the database. Additionally, runnning this code more than once will result in the same error above as it will attempt to create the same tables it created in the first run. However, in this case to fix the error you will simply need to comment out the calls to the functions that create the tables and views. These are clearly visible in the code as they are sectioned off by block comments i.e. lines of hashtags      

### Files

The files included are: 
* `reporter.py` - This file contains all Python code that acts on the news database for the reporter tool. It defines various methods that create tables or views or execute queries over the database to get the answers to the above questions.
* `README.md` 

__NOTE:__ You may need the `newsdata.sql` file containing all data in this project folder. I could not include it here as it is too large to share and store.

### Describing the Extra Views and Tables Created

Below is a list of the extra views and tables `reporter.py` creates in order to more easily find the answers to our questions. There are also descriptions of each view and table and a little bit about how and why they were created. Also, all tables and views are created within a function of the same name, unless otherwise stated below.
* __articles_and_authors *(view)*__ - Created by joining the articles and authors tables on the articles' author column and the authors' id column, so now this view has the columns: author (int), title (text), slug (text), time (timestamp with time zone), id (int), name (text), bio (text), author_id (int). This view will be useful when finding the top three authors as we will combine it with the articles_and_logs view.
* __articles_and_logs *(view)*__ - Created by combining the articles table with the newly created updated_log table through joining the tables using the articles' slug column and the updated_log's article_slug column. The columns it has are all the columns from the articles table and the updated_log table. This view is useful in solving both the questions about the top three articles and the top three authors.
* __total_and_errors *(view)*__ - Created by joining the requests_per_day table and the error_requests_per_day table on the requests_per_day date column and the error_requests_per_day e_date column. The columns here are: date (date), total_requests (int), e_date (date), num_errors (int). This will be used to solve the third question.
* __updated_log *(table)*__ - This is created in the function called `update_log()` where all information from the log table, minus the ip column, is copied into the table called updated_log. Then we alter updated_log to include an article_slug column which we then populate by extracting the articles the requests were searching for as given by the path column. Pulling out the slug's from the path allows us to join this table with the articles_and_authors view and allows us to create the articles_and_logs view critical for answering questions one and two. The columns in this table are all columns from log, except ip, and an additional column called article_slug.
* __requests_per_day *(table)*__ - To create this table we asked for the date(time) from the log column, this extracts only the date from the timestamp object, and then we count() all requests made that day by grouping our output by date(time). The columns are date (date) and total_requests (int) which is the result from the count(). This table is useful in creating the total_and_errors view necessary for the third question.
* __error_requests_per_day *(table)*__ - To create this table we again ask for the date(time) from the log column but call it e_date so that we can more easily join this table with the requests_per_day table. Then we count() all requests that day that satisfy the condition that the log's status column says '404 NOT FOUND' and we save this count as num_errors. Finally, grouping by e_date gets us the number of requests that resulted in an error. The columns are e_date (date) and num_errors (int). This table is useful in creating the total_and_errors view necessary for the third question. 
