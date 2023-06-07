import argparse
import sys, subprocess
import asyncio
import yaml

from notifier import TelegramNotifier
from meta import version

reportLinesLimit = 20

# TODO: create log file for each execution
async def main():
    parser = argparse.ArgumentParser(
        description='Util to replicate backups from primary storage to a mirrors',
    )
    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + version)

    parser.add_argument('config', help="Path to config file")

    args = parser.parse_args()

    config = yaml.load(open(args.config), Loader=yaml.Loader)

    # Configure notifier
    token = None
    users = None
    notifierPrefix = None
    if ('notifications' in config):
        token = config['notifications']['telegram']['botToken']
        users = config['notifications']['telegram']['userIds']
        notifierPrefix = config['notifications'].get('prefix')
    notifier = TelegramNotifier(token, users)
    notifier.setPrefix(notifierPrefix)

    # Run tasks
    for taskId, task in enumerate(config['tasks']):
        taskName = task['name'] if 'name' in task else task['run']
        escapedTaskName = notifier.escapeText(taskName)

        newLinePrefix = '\n' if taskId != 0 else ''
        print(newLinePrefix + f'Task "{taskName}"', flush=True)

        # Skip by condition
        if 'if' in task:
            ifCmd = subprocess.Popen(task['if'], shell=True)
            ifCmd.wait()
            if ifCmd.returncode != 0:
                print(f'Skip task "{taskName}"', flush=True)
                await notifier.notify(f'Skip task "{escapedTaskName}"')
                continue

        # Run command
        commands = task['run'] if isinstance(task['run'], list) else [task['run']]
        for cmdIndex, command in enumerate(commands):
            print(f'Run command "{command}"', flush=True)

            # TODO: add timeout to stop process
            replicationProcess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
            totalCommandsLen = len(commands)
            messageTargetSuffix = f'- command {cmdIndex + 1}/{totalCommandsLen}' if totalCommandsLen > 1 else ''
            messageTarget = f'Task "{escapedTaskName}"' + notifier.escapeText(messageTargetSuffix)

            if isRunSuccessful:
                await notifier.notify(f'{messageTarget} final successful')
            else:
                # add last few lines to explain context
                lastLog = notifier.escapeText(''.join(outLines))
                await notifier.notify(f'⚠️ {messageTarget} has failed\n\n```\n...\n{lastLog}\n```')

            # Stop the program for fails
            if not isRunSuccessful:
                exit(replicationProcess.returncode)

    # Final
    await notifier.notify(f'🎉 All tasks has final successful')


def cli():
    asyncio.run(main())

