from os.path import dirname, abspath
from invoke import task

from api.config import settings as local

BASE_DIR = dirname(abspath(__file__))


@task
def hello(ctx):
    print("Hi Swiss")


@task
def run(c):
    c.run('{}/manage.py runserver 8000'.format(BASE_DIR))


@task
def shell(c):
    c.run('{}/manage.py shell'.format(BASE_DIR))


@task
def create(c, app):
    c.run('mkdir -pv "api/{}"'.format(app))
    c.run('{}/manage.py startapp {} api/{}'.format(BASE_DIR, app, app))


@task
def migrate(c):
    c.run('{}/manage.py migrate'.format(BASE_DIR))


@task
def make(c, app):
    c.run('{}/manage.py makemigrations {}'.format(BASE_DIR, app))


@task
def commit(c):
    c.run('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')
    c.run('git add . && git commit')


@task
def pull(c):
    c.run('git merge origin/develop')
    c.run('git pull origin develop')


@task
def push(c, branch):
    commit()
    pull()
    c.run('git push origin {}'.format(branch))


def setup(c, *args):

    sudoer = '' if 'no-sudo' in args else 'sudo mysql -U root -p'
    db_name = local.DATABASES.get('default').get('NAME')
    db_user = local.DATABASES.get('default').get('USER')
    db_pass = local.DATABASES.get('default').get('PASSWORD')

    with BASE_DIR:
        c.run('{} -c "DROP DATABASE IF EXISTS {}"'.format(
            sudoer, db_name
        ))
        c.run('{} -c "CREATE DATABASE {}"'.format(sudoer, db_name))
        c.run('{0} -c "DROP USER IF EXISTS {1}"'.format(
            sudoer, db_user
        ))
        c.run(
            '{} -c "CREATE USER {} WITH SUPERUSER CREATEDB CREATEROLE '
            'LOGIN PASSWORD \'{}\'"'.format(sudoer, db_user, db_pass)
        )
        c.run('{} -c  "CREATE EXTENSION IF NOT EXISTS pg_trgm"'.format(
            sudoer
        ))
        c.run('python manage.py migrate')
