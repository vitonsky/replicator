Replicate master backup to mirror targets

To use util, first create replication YAML file with such structure
```yml
# Notifications config
notifications:
    telegram:
        # Token for bot who will sent notifications
        botToken: '123:token'
        # User IDs to receive notifications
        userIds:
            - 123456

# Replication description
tasks:
    - source: 'privateS3:/backups'
      mirrors:
        - /path/to/local/mirror1
        - /path/to/local/mirror2
        - s3Mirror1:backups
        - s3Mirror2:backups
```

## TODO
- [x] Support few entries for replication
- [ ] Provide commands to run, instead of paths
- [ ] Provide instructions to install as binary
- [ ] Split the code