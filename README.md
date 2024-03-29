# Digital Services System (Namely Digital Life) for No.2 High School of East China Normal University

Built by [aeilot](https://aeilot.top) and [xiaoyaowudi](https://www.xiaoyaowudi.com).

## 贡献须知 | Notice for assistant technicians

所有干事都必须创建 PR 进行代码修改！！！不得直接在主 branch 上 commit！！！谢谢！

Assistants MUST not directly commit changes to the main branch. It's proposed that they create PRs to propose a change.

## Installation

Run the following codes:

```bash
pip install -r requirements.txt
```

## Usage

Setup DB: (We are using MariaDB/MySQL as the database)

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
