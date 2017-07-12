[![Coverage Status](https://coveralls.io/repos/github/jdepoix/goto_cloud/badge.svg?branch=development)](https://coveralls.io/github/jdepoix/goto_cloud?branch=development) [![Build Status](https://travis-ci.org/jdepoix/goto_cloud.svg?branch=development)](https://travis-ci.org/jdepoix/goto_cloud) [![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](http://opensource.org/licenses/MIT)
# goto cloud; Making Cloud Migration easy

## Early Access
To try this out, follow these steps.

### Current Limitations
Currently the only supported cloud provider is Profitbricks. Also only migrating systems running Ubuntu 12.04-16.04 is
supported. It could still work on other Linux distros, but it's only been tested against them.

### Requirements
You need to have postgres >= 9.4 and rabbitmq running.

### Install dependencies
First create a new python3 virtualenv and install the dependencies, in the root directory of this project:

```
python3 -m venv virtualenv
virtualenv/bin/pip install -r requirements/local.txt
```

### Configure django
Now make a copy of the `secrets.template.json` which should be called `secrets.json` and enter the credentials needed:
```
cp secrets.template.json secrets.json
vim secrets.json
...
```
and now run the migrations: 
```
./manage.py migrate
```

### Start Celery
Start celery by running:
```
virtualenv/bin/celery -A goto_cloud.settings.celery worker --loglevel=info --logfile=migration.log
```

### Configure your migration plan
Open and edit the file `tryout_migration_plan.py`. The file contains a dict which controls the actions which are take during
the migration. It contains comments which should make clear how set things up. In case you need more information, on how to
configure it, feel free to ask me. But you probably need to be at least somewhat familiar, with how the migration 
process works. It will be better documented in future releases for sure.

### Create your hook scripts
In case you want to use hooks in your migration plan, put them in the folder `test_scripts` and use the file name in the
migration plan. Hook script file names in the migration plan are always interpreted relative to the `test_scripts` 
folder. They all should contain valid python2 code. At runtime a dict called `CONTEXT` will be injected into the script,
which contains information about the ongoing migration and should help you write more useful hook scripts.

### Make sure source and target machine are ready for the migration
For the migration to work successfully a few things have to been taken care of, before starting the migration:
- The management server (probably your local machine, if your trying this out) should have ssh access to the source, as 
well as the target machine. To make sure it has access to the target machine, just make sure it has access to the
machine, you take the snapshot of, which will be used as the bootstrapping template.
- The source needs to have ssh access to the target machine

### Start the migration
After everything is setup, you can start the migration. Just run `./tryout_migrate.py`, go get a coffee and see what 
happened, when you come back.

You can tail the file `migration.log`, to see what's going on, during the migration.

### Retrying migration for individual sources
If the migration on a given source fails, you can restart the migration for just this source, by running the following 
command:

`./tryout_retry_source_migration.py <SOURCE_ID>`

If you don't know the ID of the source you want to restart, then just run the command without a parameter. When doing so
a list of all sources, which are not live yet and the state they currently reside in, are printed.

### Go live
After the migration has finished, you can trigger the go live. This will remove the bootstrapping volume and network 
interface and boot into the actual system. The go live script is started, with an ID, referencing the migration. The ID 
of the migration, was printed out during the migration. Then run:

`./tryout_go_live.py <MIGRATION_ID>`

Have fun and let me know what you think of it!
