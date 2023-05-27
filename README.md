Replicate master backup to mirror targets

To use util, first create replication YAML file.

Example config on local device
```yml
# Notifications config
notifications:
    telegram:
        # Define should notifications been sent
        enabled: false
        # Token for bot who will sent notifications
        botToken: '123:token'
        # User IDs to receive notifications
        userIds:
            - 123456

# Task may have name
tasks:
    - name: 'Copy files to disk'
      run: rclone ./backups /path/to/local/mirror1

    - name: 'Upload to S3'
      run: rclone ./backups s3Replica:backups

    - name: 'Replicate on server'
      # Just run replicator on server and stop
      run: ssh replicator@backup-server 'nohup replicator ./backups.yml > ./replicator.log 2>&1 </dev/null &'
```

Config example on backup server
```yml
# Notifications config
notifications:
    telegram:
        # Define should notifications been sent
        enabled: true
        # Token for bot who will sent notifications
        botToken: '123:token'
        # User IDs to receive notifications
        userIds:
            - 123456

# Replication description
tasks:
    - run: rclone s3Replica:backups s3Mirror1:backups
    - run: rclone s3Replica:backups s3Mirror2:backups
    - run: rclone s3Replica:backups s3Mirror3:backups
```

## TODO
- [x] Support few entries for replication
- [x] Provide commands to run, instead of paths
- [ ] Provide instructions to install as binary
- [ ] Split the code