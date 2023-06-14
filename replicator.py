import argparse
import os
import sys, subprocess
import asyncio
import yaml

from notifier import TelegramNotifier
from meta import version

reportLinesLimit = 20

taskFileName = 'Taskfile.yml'

# TODO: create log file for each execution
async def main():
    parser = argparse.ArgumentParser(
        description='Util to replicate backups from primary storage to a mirrors',
    )
    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + version)
    parser.add_argument('--config', '-c', help="Path to config file")
    parser.add_argument('tasks', help="Task names to run", nargs="*")

    args = parser.parse_args()

    configFilePath = args.config if args.config is not None else os.path.join(os.getcwd(), taskFileName)
    if os.path.exists(configFilePath) is False:
        print(f'Not found task file by path "{configFilePath}"')
        exit(1)

    config = yaml.load(open(configFilePath), Loader=yaml.Loader)

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
    for taskName, task in config['tasks'].items():
        # TODO: Filter tasks before iterate
        if len(args.tasks) > 0 and taskName not in args.tasks: continue

        for subtaskId, subtask in enumerate(task):
            subtaskName = subtask['name'] if 'name' in subtask else subtask['run']
            escapedTaskName = notifier.escapeText(subtaskName)

            newLinePrefix = '\n' if subtaskId != 0 else ''
            print(newLinePrefix + f'Task "{subtaskName}"', flush=True)

            # Skip by condition
            if 'if' in subtask:
                ifCmd = subprocess.Popen(subtask['if'], shell=True)
                ifCmd.wait()
                if ifCmd.returncode != 0:
                    print(f'Skip task "{subtaskName}"', flush=True)
                    await notifier.notify(f'Skip task "{escapedTaskName}"')
                    continue

            # Run command
            commands = subtask['run'] if isinstance(subtask['run'], list) else [subtask['run']]
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

