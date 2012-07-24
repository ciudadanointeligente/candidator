Candideit.org
============


Candideit.org is a simple application that aims to provide comparable information about the positions of candidates to any election.

The living application can be found at [www.candideit.org](http://www.candideit.org)


Requirements
============
* [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/)

       In ubuntu is as easy as 

       ```
       sudo apt-get install virtualenvwrapper
       ```
* [Python Imaging Library PIL](http://www.pythonware.com/products/pil/)

If you are using ubuntu 12.04 you can [follow this guide](http://www.sandersnewmedia.com/why/2012/04/16/installing-pil-virtualenv-ubuntu-1204-precise-pangolin/).



Instalation instructions
================================

Step 1:
-------

Create a python virtualenvironment

```
mkvirtualenv candideit
```

Step 2:
-------
Clone the project from our repo

```
git clone git@github.com:ciudadanointeligente/candidator.org.git candidator
```

Enter the directory

```
cd candidator
```

If you are going to be developing candideit you should move to the dev branch

```
git checkout dev
```	

Step 3:
-------

Install dependencies.

```
pip install -r requirements.txt
```

Step 4:
-------

Run tests

```
python manage test elections
```

It runs all tests in the elections application

Step 5:
-------

Sync database

```
python manage syncdb
```

We are using sqlite3 to store all the data but if you would like to use another database you are free to do so, and it can be changed in 'settings.py'.


Step 6:
-------

Run the application

```
python manage runserver
```


Instalation troubleshooting
================================

6 failing tests
---------------
It is due to PIL not installed with JPEG support you can [follow this guide](http://www.sandersnewmedia.com/why/2012/04/16/installing-pil-virtualenv-ubuntu-1204-precise-pangolin/).


Testing
=======

* To run all tests


   ```
   python manage test elections
   ```

* To check code coverage

   ```
   python manage.py test_coverage elections
   ```