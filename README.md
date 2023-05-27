Replicator is a task runner for backups.

You can describe your tasks declarative with YAML file and run task files with CRON.

Replicator supports notifications, it's useful for tasks that take a lot of time.

## Install

- Clone repository `git clone https://github.com/vitonsky/replicator.git`
- Build package with run `make build`
- Install package `pip install dist/replicator-0.0.1-py3-none-any.whl`

## Usage

```
usage: replicator [-h] config

Util to replicate backups from primary storage to a mirrors

positional arguments:
  config      Path to config file

optional arguments:
  -h, --help  show this help message and exit
```

To use util, first create task file.

Example task file for a local device
```yml
tasks:
    # Task may have name
    - name: 'Copy files to backup disk'
      run: rclone ./backups /path/to/local/mirror1

    - name: 'Upload to S3'
      run: rclone ./backups s3Replica:backups

    - name: 'Replicate on server'
      # Just run replicator on server with their own config and end locally
      run: ssh replicator@backup-server 'nohup replicator ./backups.yml > ./replicator.log 2>&1 </dev/null &'
```

Example task file for backup server
```yml
# Notifications config
notifications:
    telegram:
        # Define should notifications been sent
        enabled: true
        # Token for bot who will sent notifications
        # How to: https://core.telegram.org/bots/tutorial#getting-ready
        botToken: '123:token'
        # User IDs to receive notifications
        userIds:
            - 123456

# Replicate backup from main storage
tasks:
    - run: rclone s3Replica:backups s3Mirror1:backups
    - run: rclone s3Replica:backups s3Mirror2:backups
    - run: rclone s3Replica:backups s3Mirror3:backups
```

## TODO
- [x] Support few entries for replication
- [x] Provide commands to run, instead of paths
- [x] Provide instructions to install as binary
- [ ] Split the code
- [ ] Add docker image