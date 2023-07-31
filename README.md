# Course Selection System for No.2 High School of East China Normal University

Build by [xiaoyaowudi](https://www.xiaoyaowudi.com), modified by [aeilot](https://aeilot.top).

## Installation

Run the following codes:

```bash
pip install -r requirements.txt
```

## Usage

Setup DB: (We are using MariaDB as the database)

Before this step, make sure you've set up a local DB server and made changes in the `club_main/settings.py` file. (Specify the server info)

```bash
python manage.py makemigrations club
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Run the server:

```bash
python manage.py runserver
```
And that's it!
