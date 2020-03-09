"""This module contains the GeneFlow ShellWrapper class."""

import os
from subprocess import (PIPE, Popen)

from geneflow.log import Log

class ShellWrapper:
    """This class interacts with the BASH/Unix shell."""

    @staticmethod
    def invoke(command):
        """
        Invoke command and return STDOUT.

        Args:
            command: The command to be invoked.

        Returns:
            On success: STDOUT.
            On failure: False.

        """
        proc = None
        try:
            proc = Popen(command, stdout=PIPE, shell=True, env=os.environ)
        except OSError as err:
            Log.an().error('invoke command failed: %s [%s]', command, str(err))
            return False

        proc.wait()
        if (proc.returncode != 0):
            Log.an().error(
                'invoke command returned non-zero exit code: %s [%s]',
                command,
                proc.returncode
            )
            return False

        stdout = proc.stdout.read()
        return stdout


    @staticmethod
    def spawn(command):
        """
        Spawn a process and return it.

        Args:
            command: The command to spawn a process.

        Returns:
            The result of Popen, or raises an exception.

        """
        try:
            return Popen(command, shell=True, env=os.environ)
        except OSError as err:
            Log.an().error('spawn command failed: %s [%s]', command, str(err))
            return False


    @staticmethod
    def is_running(proc):
        """
        Check if process is running.

        Args:
            proc: The process object for which status is to be returned.

        Returns:
            The result of proc.poll() check, or raises an exception.

        """
        return proc.poll() is None
