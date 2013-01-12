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
git clone git@github.com:ciudadanointeligente/candidator.git candidator
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

Translation and internationalization
====================================


## Getting started

If you run ```python manage.py runserver``` and ```open http://127.0.0.1:8000/``` you should see the Spanish version in your browser.

Create a `local_settings.py` file, and edit settings as appropriate:

```sh
cp local_settings.py.example local_settings.py
```

## Creating a new translation

The following commands assume your locale code is `en`. Replace it as appropriate with the [ISO 639-1 code](http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for your locale. The locale code you choose below must match the `LANGUAGE_CODE` in `local_settings.py`.

### Manually

First, create or update the `django.po` file for your locale:

```sh
django-admin.py makemessages -l en
```

You will find the file in `locale/en/LC_MESSAGES`. You can now edit the `.po` file by hand or with a variety of editors.

### Transifex

You may prefer to use [Transifex](https://www.transifex.com/) to translate the `.po` file:

* Go to Candideit's [Transifex page](https://www.transifex.com/projects/p/candideit/resource/django-po/)
* Click "Add new translation"
* Select your language and click "Translate online"

Once your translations are done, notify a Candideit maintainer, and they can pull your translations into the project.

## Important reminders

* Keep the same case: translate "NOMBRE DE LA ELECCIÓN:" as "ELECTION NAME:" not "Election name:"
* Keep all punctuation: translate "NOMBRE DE LA ELECCIÓN:" as "ELECTION NAME:" not "ELECTION NAME"

## Using your translations

To use your translation, you need to compile the `.po` file to a `.mo` file:

```sh
python manage.py compilemessages
```
