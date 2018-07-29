Programming Assignment 2
 Introduction to Relational DB, SQL (Cloud)
 Due: In Blackboard
 Task: You will get world earthquake data, import into SQL and with a web interface
allow users to find out (query) interesting information about those earthquakes.
 Description:
 Your assignment is to provide a local interface to a cloud service that you will
 implement that will allow a user to upload earthquake data and investigate it.
Please go to:
https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php
and get all earth quakes for the last 30 days (bottom right), a .csv file,
place these on your cloud service provider and import this into SQL.
This page also has a “schema” for the data.
And your cloud-based “service” will allow a user to:
+ Search for and count all earthquakes that occurred with a magnitude greater
 than 5.0
+ Search for 2.0 to 2.5, 2.5 to 3.0… for a week a day or the whole 30 days.
+ Find earthquakes that were near (20 km, 50 km?) of a specified location.
+ Find clusters of earthquakes
+ Do large (>4.0 mag) occur more often at night?
And similar…
In later work you will try to “learn” from the data and show graphs and pictures.
Not yet (unless you want to).
You will use some type of RDB SQL to store and retrieve earthquake information.
And (of course) a friendly web UI.
You should handle conditions such as: missing data (fields, attributes), and similar. 