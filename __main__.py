#!/usr/bin/env python3

import argparse
import sys, subprocess
import asyncio
import telegram
import yaml

reportLinesLimit = 20

# TODO: create log file for each execution
async def main():
    parser = argparse.ArgumentParser(
        description='Util to replicate backups from primary storage to a mirrors')

    parser.add_argument('config', help="Path to config file")

    args = parser.parse_args()

    config = yaml.load(open(args.config), Loader=yaml.Loader)

    # Configure bot
    bot = telegram.Bot(config['notifications']['telegram']['botToken'])
    # async with bot:
    #     print(await bot.get_me())

    sourceStorage = config['replication']['source']
    mirrors = config['replication']['mirrors']

    for mirror in mirrors:
        print(f"Replicate {sourceStorage} to {mirror}")

        # Run command
        # TODO: add timeout to stop process
        # TODO: provide commands
        # cmd = ['bash', '-c', 'echo 1 && echo 2']
        cmd = ['rclone', 'sync', '-P', '--retries-sleep', '700ms', '--max-backlog', '10', '--transfers', '4', sourceStorage, mirror]
        replicationProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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

        # Notify result
        async with bot:
            for userId in config['notifications']['telegram']['userIds']:
                if replicationProcess.returncode == 0:
                    await bot.send_message(text=f'Replication to mirror "{mirror}" final successful', chat_id=userId)
                else:
                    # add last few lines to explain context
                    lastLog= ''.join(outLines)
                    await bot.send_message(text=f'⚠️ Replication to mirror "{mirror}" are failed\n\n```\n...\n{lastLog}\n```', chat_id=userId, parse_mode='MarkdownV2')


if __name__ == '__main__':
    asyncio.run(main())