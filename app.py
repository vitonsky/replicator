import argparse
import sys, subprocess
import asyncio
import yaml

from notifier import TelegramNotifier

reportLinesLimit = 20

# TODO: create log file for each execution
async def main():
    parser = argparse.ArgumentParser(
        description='Util to replicate backups from primary storage to a mirrors')

    parser.add_argument('config', help="Path to config file")

    args = parser.parse_args()

    config = yaml.load(open(args.config), Loader=yaml.Loader)

    # Configure notifier
    notifier = None
    if ('notifications' in config):
        token = config['notifications']['telegram']['botToken']
        users = config['notifications']['telegram']['userIds']

        notifier = TelegramNotifier(token, users)

    # Run tasks
    for task in config['tasks']:
        taskName = task['name'] if 'name' in task else task['run']

        print(f'Run command "{taskName}"', flush=True)

        # Run command
        # TODO: add timeout to stop process
        cmd = task['run']
        replicationProcess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        outLines = []
        for rawLine in iter(replicationProcess.stdout.readline, b''):
            line = rawLine.decode('utf-8')

            # Print output to console
            sys.stdout.write(line)

            # Remove old lines out of limit
            if (reportLinesLimit > 0):
                freeSlots = reportLinesLimit - len(outLines)
                if (freeSlots <= 0):
                    slotsToRemove = -freeSlots + 1
                    outLines = outLines[slotsToRemove:]

            # Add lines
            outLines.append(line)
        replicationProcess.stdout.close()
        replicationProcess.wait()

        isRunSuccessful = replicationProcess.returncode == 0

        # Notify result
        if notifier is not None:
            notifications = config['notifications']
            notificationPrefix = '*' + notifications['prefix'] + '*: ' if 'prefix' in notifications else ''

            escapedTaskName = notifier.escapeText(taskName)
            if isRunSuccessful:
                await notifier.notify(notificationPrefix + f'Task "{escapedTaskName}" final successful')
            else:
                # add last few lines to explain context
                lastLog = notifier.escapeText(''.join(outLines))
                await notifier.notify(notificationPrefix + f'⚠️ Task "{escapedTaskName}" are failed\n\n```\n...\n{lastLog}\n```')

        # Stop the program for fails
        if not isRunSuccessful:
            exit(replicationProcess.returncode)


def cli():
    asyncio.run(main())

