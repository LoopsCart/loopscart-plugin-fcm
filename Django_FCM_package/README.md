## Pyenv virtual environment setup
```sh
    pyenv install 3.13.3 FCM_package_env
    pyenv local FCM_package_env
```

pip install firebase-admin

## setting up database in the local computer
```sql

CREATE DATABASE FCM_db;

CREATE USER fcm_user WITH PASSWORD 'firebase-cloud-messaging-server-database-password123#';

GRANT ALL PRIVILEGES ON DATABASE FCM_db TO fcm_user;

ALTER ROLE fcm_user SET client_encoding TO 'utf8';
ALTER ROLE fcm_user SET default_transaction_isolation TO 'read committed’;
ALTER ROLE fcm_user SET timezone TO 'UTC';
```

## for LSP
pip install django-stubs
pip install "djangorestframework-stubs[compatible]

## for building (maynot be required)
pip install build
pip install setuptools
