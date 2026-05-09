**CS5330 Group 2 Project**

Created by Vikas Deo, Emilio Munoz, Asha Patel, and Savannah Nelson.

This application is a desktop tool for storing and querying social media post and research anaylsis results.
It uses a MySQL database as the backend, and a Python desktop window (GUI) as the frontend.

The app is organized into three sections:
- Data Entry
- Search Posts
- Experiments

*User manual for installation and program use:*

Overview

Welcome to our application! Our application uses a MySQL database on your local machine as the backend and a Python desktop window (GUI) as the frontend. You do not need any database knowledge to use it - just follow these steps in this manual.

Installation

Follow these steps in order. Do them once on your machine before running the app.

Step 1 - Install Python

Python is the programming language the app is written in.
Open your web browser and go to: https://www.python.org/downloads/
Click the big yellow Download button
Open the downloaded file and follow the installer
When finished, open a Terminal window and type:

| python3 - - version

You should see something like Python 3.x.x. If so, Python is installed correctly.
Note: On Windows use python instead of python3 throughout this manual

Step 2 - Install MySQL

My SQL is the database engine that stores all the data. 

Go to: https://dev.mysql.com/

Under “Select Operating System” choose your OS (macOS or Windows)

Download the DMG (macOS) or MSI (Windows) installer - the one labeled “DMG Archive” or “Windows (x86, 64-bit)”

Run the installer and follow all the default steps

At the end, the installer will ask you to set a root password (Important to write the password down, you will use it later)

After installation, open a new Terminal and type:

| mysql - - version

If it says “command not found” on Mac, try the full path:

| usr/local/mysql/bin/mysql - - version

*Note: The root password is your MySQL admin password, not your computer login password*

Step 3 - Install the Python MySQL connector

This is a small add-on that lets Python talk to MySQL.

Install it by running:

	| pip3 install mysql-connector-python
	
You should see “Successfully installed” at the end. If you see “Requirement already satisfied” that is fine too!

Step 4 - Download the Project

Go to the GitHub rep link provided to you, or for our project: 
https://github.com/Gitlio11/cs5330-group-project/tree/main

Click the green Code button

Click Download ZIP

Unzip the downloaded file - you will get a folder called cs5330-group-project-main

Step 5 - Create the Database

You need to create the database and set up all the tables. 

5a. Create the database

In Terminal run (use the full path on Mac if needed)

	| mysql -u root -p -e “CREATE DATABASE social_media_db;”
	
	Type your MySQL root password when asked!

5b. Run the schema

Navigate into the project folder, then run the schema file:

	| cd Downloads/cs5330-group-project-main
	
	| mysql -u root -p social_media_db < schema.sql
	
	This creates all the tables. You shouldn’t see any errors.
	
*Note: If you get “Unknown database” when running 5b, make sure you ran 5a first.*

Step 6 - Configure Your Database Credentials

Open the file in the project folder called db_config.txt inside the project folder. Edit it so it contains your actual MySQL password, you should not need to change anything else:

	| username=root
	
	| password=YOUR_MYSQL_PASSWORD_HERE
	
	| database=social_media_db
	
	| host=localhost
	
	| port=3306
	
	Be sure to save the file.


  
