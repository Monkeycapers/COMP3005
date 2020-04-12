# COMP3005
COMP3005 Book Store Project

# Dependencies
Flask
Flask-Login
Flask-Bcrypt

All dependencies can be seen in requirements.txt.

To install dependencies:
0) It is reccomended you make a virtual envrionment of some sort
1) pip install -r requirements.txt

Running:
./run-app.sh (bash + linux required)

Configuring the database:
In the connect method in database.py, change the database connection string

Running Admin.py:

./Admin.py with no arguments to use the add/remove loop
It is reccomended to use input redirection for the loop
(e.g) ./Admin.py < sampleAdminInput.txt
Any image file names specified should have a corresponding file in Static/imgs/filename.jpg
./Admin.py -hardreset - init the database and remove any existing tables (required if starting from new db)

note: if you are using the sampleAdminInput.txt it is your responsibilty to source images and place them in Static/imgs (I cannot distribute images due to copyright)