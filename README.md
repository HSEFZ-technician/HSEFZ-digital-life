# Digital Services System (Namely Digital Life) for No.2 High School of East China Normal University

Built by [aeilot](https://aeilot.top) and [xiaoyaowudi](https://www.xiaoyaowudi.com).

## 贡献须知 | Notice for assistant technicians

所有干事都必须创建 PR 进行代码修改！！！不得直接在主 branch 上 commit！！！提交代码前请在本地测试！！！谢谢！

Assistants MUST not directly commit changes to the main branch. It's proposed that they create PRs to propose a change. Please test locally before submitting the code. 

## Installation

Clone the repository:

```bash
git clone https://github.com/HSEFZ-technician/HSEFZ-digital-life.git
```

Run the following command:

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
If migration fails, please refer to [this solution](https://stackoverflow.com/questions/27583744/django-table-doesnt-exist). 

Create superuser:

```bash
python manage.py createsuperuser
```

Run the server:

```bash
python manage.py runserver
```

And that's it!

## Selection system usage

Please test locally before changing the database on the server. 

Log in to the MySQL database:
```bash
mysql -u root -p
```

Select the database:
```bash
use selection_users;
```

Set yourself as a superuser and staff:
```bash
update club_studentclubdata
set is_superuser=1, is_staff=1
where email='your email';
```

Create a new selection event (or use django admin: url/admin):
```bash
insert into club_selectionevent(id, start_time, end_time, title)
values(value1, value2, value3, 'title');
```

Create a new set of events (or use django admin: url/admin): 
```bash
insert into club_eventclasstype(id, type_name, event_id_id)
values(value1, 'title', value2);
```

Create a new group (or use django admin: url/admin):
```bash
insert into auth_group(id, name)
values(value1, 'group_name');
```
Create a new line in club_eventclasstypeconstraints:
```bash
insert into club_eventclasstypeconstraints(id, coef_1, coef_2, C, type_id1_id, type_id2_id, event_id_id)
values(value1, 1, 1, 2, first_event_class_type, second_event_class_type, event_id);
```

Save new students to the database:

Upload a csv that contains the students' name, email and student_id.

Then quit mysql and run the following script.
```bash
python3 add_users.py
```

Save new students to the corresponding group:

First change the group_id and database configuration in `add_group.py`.
```bash
python3 add_group.py
```

Authorize club leaders to edit their club information:

First change the database configuration in `add_managers.py`.

Then change the emails in managers.txt.
```bash
python3 add_managers.py
```

After the selection ends, export the selection data:
```bash
python3 check_users.py
```

And that's it!
