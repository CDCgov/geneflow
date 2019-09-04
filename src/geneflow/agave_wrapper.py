"""This module contains the GeneFlow AgavePyWrapper and helper classes."""

import os
import time
import urllib.parse

try:
    from agavepy.agave import Agave
    from agavepy.asynchronous import AgaveAsyncResponse
except ImportError: pass

from geneflow.log import Log

class AgavePyWrapper:
    """Wraps AgavePy to enable retries and multi-process token handling."""

    def __init__(self, agave, config, retry, retry_delay):
        """
        Initialize AgavePyWrapper class.

        Args:
            self: class instance.
            agave: Agave connection object returned by AgavePy.
            config: the Agave subsection of the GeneFlow configuration.
            retry: Number of retries.
            retry_delay: Delay between retry attempts (seconds).

        Returns:
            AgavePyWrapper instance.

        """
        self._agave = agave
        self._config = config
        self._retry = retry
        self._retry_delay = retry_delay


    def call(self, *args, **kwargs):
        """
        Wrap function for executing an AgavePy command.

        Args:
            self: class instance.
            *args: Any arguments to be sent to the agavePy command.
            **kwargs: Any keyword-value arguments to be sent to the agavePy
                command.

        Returns:
            result of the agavePy command call.

        """
        num_tries = 0
        num_token_tries = 0
        while (
                num_tries < self._retry
                and num_token_tries < self._config['token_retry']
        ):

            try:
                try:
                    result = self._call(*args, **kwargs)
                    return result

                except Exception as err:
                    # check for expired token error
                    if '401' in str(err):
                        num_token_tries += 1
                        Log.a().warning('agave token error [%s]', str(err))
                        time.sleep(self._config['token_retry_delay'])

                        # token could not be refreshed, most likely because
                        # token was refreshed in a different thread/process

                        # create new token
                        if self._config['connection_type'] == 'impersonate':
                            # re-init object without losing object binding
                            self._agave.__init__(
                                api_server=self._config['server'],
                                username=self._config['username'],
                                password=self._config['password'],
                                token_username=self._config['token_username'],
                                client_name=self._config['client'],
                                api_key=self._config['key'],
                                api_secret=self._config['secret'],
                                verify=False
                            )

                        elif self._config['connection_type'] == 'agave-cli':
                            # get updated credentials from ~/.agave/current
                            agave_clients = Agave._read_clients()
                            # don't verify ssl
                            agave_clients[0]['verify'] = False
                            # re-init object without losing object binding
                            self._agave.__init__(**agave_clients[0])

                        else:
                            # shouldn't reach this condition, but raise
                            # exception just in case
                            raise Exception(
                                'invalid agave connection type: {}'.format(
                                    self._config['connection_type']
                                )
                            )

                    if '404' in str(err):
                        # don't retry if 404 error
                        return False

                    # not a token error, re-raise
                    raise err

            except Exception as err:
                num_tries += 1
                Log.a().warning('agave call failed [%s]', str(err))
                time.sleep(self._retry_delay)

        if num_token_tries == self._config['token_retry']:
            # failed after reaching token refresh attempt limit
            Log.an().error(
                'agave token refresh max tries (%s) exceeded',
                self._config['token_retry']
            )
            return False

        if num_tries == self._retry:
            # failed due to other exceptions
            Log.an().error('agave call max tries (%s) exceeded', self._retry)
            return False

        return result


    def _call(self, *args, **kwargs):
        """
        Override child class methods that make the actual agavePy call.

        Args:
            self: class instance.
            *args: Any arguments to be sent to the agavePy command.
            **kwargs: Any keyword-value arguments to be sent to the agavePy
                command.

        Returns:
            Result of AgavePy call.

        """
        raise NotImplementedError


class AgaveFilesDownload(AgavePyWrapper):
    """
    Recursively download Agave files/folders.

    Wraps AgavePy file listing and file download operations.

    Parent class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesDownload class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class instance.

        """
        super(AgaveFilesDownload, self).__init__(
            agave,
            config,
            retry=2,
            retry_delay=0
        )


    def _recursive_download(self, systemId, filePath, targetPath, depth):
        """
        Recursively download files from an Agave location.

        Args:
            self: class instance.
            systemId: Agave system to download from.
            filePath: Agave path of file or folder to download.
            targetPath: local directory path for download target.
            depth: recursion depth: -1=all, 0=nothing, 1=file or
                directory and all files under it

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        if depth == 0:
            # done downloading to specified depth
            return True

        files = self._agave.files.list(
            systemId=systemId,
            filePath=filePath,
            limit=1000000
        )
        for file in files:
            if file['name'] == '.':
                # create directory at target location
                os.makedirs(targetPath)
                continue

            if file['type'] == 'file':
                # download file
                agave_uri = None
                local_uri = None
                if len(files) > 1:
                    agave_uri = 'agave://{}{}/{}'.format(
                        systemId, filePath, file['name']
                    )
                    local_uri = os.path.join(targetPath, file['name'])

                else:
                    # toplevel target is a file
                    agave_uri = 'agave://{}{}'.format(systemId, filePath)
                    local_uri = targetPath

                try:
                    self._agave.download_uri(
                        agave_uri, local_uri
                    )

                except Exception as err:
                    Log.an().error(
                        'download FAILED: %s -> %s [%s]',
                        agave_uri,
                        local_uri,
                        str(err)
                    )
                    return False

                Log.some().debug(
                    'download FINISHED: %s -> %s',
                    agave_uri,
                    local_uri
                )

            else:
                # recursively download the folder
                self._recursive_download(
                    systemId,
                    '{}/{}'.format(filePath, file['name']),
                    os.path.join(targetPath, file['name']),
                    depth-1 if depth != -1 else -1
                )

        return True


    def _call(self, systemId, filePath, targetPath, depth=-1):

        return self._recursive_download(systemId, filePath, targetPath, depth)


class AgaveFilesList(AgavePyWrapper):
    """
    Wraps AgavePy file listing operation.

    Parent class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesList class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class instance.

        """
        super(AgaveFilesList, self).__init__(
            agave,
            config,
            retry=config['files_list_retry'],
            retry_delay=config['files_list_retry_delay']
        )


    def _call(self, systemId, filePath):
        """
        Wrap agavePy file listing command.

        Args:
            self: class instance
            systemId: Identifier for Agave storage system
            filePath: Path for file listing

        Returns:
            List of file names

        """
        files = [
            {
                'name': f.name,
                'type': f.type
            } for f in self._agave.files.list(
                systemId=systemId,
                filePath=filePath,
                limit=1000000
            ) if f.name[:1] != '.' # skip files that start with .
        ]

        return files


class AgaveFilesDelete(AgavePyWrapper):
    """
    Wraps AgavePy file deletion operation.

    Parent class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesDelete class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            False

        """
        super(AgaveFilesDelete, self).__init__(
            agave,
            config,
            retry=config['files_delete_retry'],
            retry_delay=config['files_delete_retry_delay']
        )


    def _call(self, systemId, filePath):
        """
        Wrap agavePy file delete command.

        Args:
               self: class instance
            systemId: Identifier for Agave storage system
            filePath: Path for file to be deleted

        Returns:
            True

        """
        self._agave.files.delete(
            systemId=systemId,
            filePath=filePath
        )

        return True


class AgaveFilesMkDir(AgavePyWrapper):
    """
    Wraps AgavePy directory creation operation.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesMkDir class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            False

        """
        super(AgaveFilesMkDir, self).__init__(
            agave,
            config,
            retry=config['mkdir_retry'],
            retry_delay=config['mkdir_retry_delay']
        )


    def _call(self, systemId, filePath, dirName):
        """
        Wrap agavePy make directory command.

        Args:
            self: class instance
            systemId: Identifier for Agave storage system
            filePath: Path where directory to be created
            dirName: Name of new directory to be created

        Returns:
            True

        """
        self._agave.files.manage(
            systemId=systemId,
            filePath=filePath,
            body={
                'action': 'mkdir',
                'path': dirName
            }
        )

        return True


class AgaveJobsSubmit(AgavePyWrapper):
    """
    Wraps AgavePy job submission operation.

    Parent class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveJobsSubmit class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
               False

        """
        super(AgaveJobsSubmit, self).__init__(
            agave,
            config,
            retry=config['job_submit_retry'],
            retry_delay=config['job_submit_retry_delay']
        )


    def _call(self, body):
        """
        Wrap agavePy submit job command.

        Args:
            self: class instance
            body: job template to be submitted

        Returns:
            job object

        """
        job = self._agave.jobs.submit(body=body)

        return job


class AgaveFilesImportDataFromLocal(AgavePyWrapper):
    """
    Wraps AgavePy import data files operation for local-to-Agave imports.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesImportDataFromLocal class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class Instance

        """
        super(AgaveFilesImportDataFromLocal, self).__init__(
            agave,
            config,
            retry=config['import_retry'],
            retry_delay=config['import_retry_delay']
        )


    def _call(self, systemId, filePath, fileName, fileToUpload):
        """
        Wrap agavePy import data file command.

        Args:
            self: class instance
            systemId: Identifier for Agave storage system
            filePath: Path where file is to be imported
            fileName: Name of the imported file
            fileToUpload: File or folder path to upload to Agave

        Returns:
            On success: True.
            On failure: False.

        """
        if os.path.isdir(fileToUpload):
            # create target directory, which is "fileName"
            agwrap_mkdir = AgaveFilesMkDir(self._agave, self._config)
            if not agwrap_mkdir.call(systemId, filePath, fileName):
                Log.an().error(
                    'cannot create folder at uri: agave://%s%s/%s',
                    systemId, filePath, fileName
                )
                return False

            # walk through local directory structure
            for root, dirs, files in os.walk(fileToUpload, topdown=True):
                # upload each file in this directory level
                for name in files:
                    # translate local path to dest path
                    dest_file_path = os.path.join(
                        filePath, fileName, root[len(fileToUpload)+1:]
                    )
                    # read file in binary mode to transfer
                    response = self._agave.files.importData(
                        systemId=systemId,
                        filePath=dest_file_path,
                        fileName=name,
                        fileToUpload=open(
                            '%s/%s' % (root, name), "rb"
                        )
                    )
                    async_response = AgaveAsyncResponse(self._agave, response)
                    status = async_response.result()
                    Log.some().debug(
                        'import %s: %s/%s -> agave://%s/%s/%s',
                        str(status),
                        root,
                        name,
                        systemId,
                        dest_file_path,
                        name
                    )
                    if status != 'FINISHED':
                        return False

                # create new directory for each directory in this level
                for name in dirs:
                    # translate local path to dest path
                    dest_file_path = os.path.join(
                        filePath, fileName, root[len(fileToUpload)+1:]
                    )
                    # create dest directory
                    if not agwrap_mkdir.call(
                            systemId,
                            dest_file_path,
                            name
                    ):
                        Log.an().error(
                            'cannot create folder at uri: agave://%s%s/%s',
                            systemId,
                            dest_file_path,
                            name
                        )
                        return False

        elif os.path.isfile(fileToUpload):
            # import single file
            response = self._agave.files.importData(
                systemId=systemId,
                filePath=filePath,
                fileName=fileName,
                fileToUpload=open(fileToUpload, 'rb')
            )
            async_response = AgaveAsyncResponse(self._agave, response)
            status = async_response.result()
            Log.some().info(
                'import %s: %s -> agave://%s/%s/%s',
                str(status),
                fileToUpload,
                systemId,
                filePath,
                fileName
            )
            if status != 'FINISHED':
                return False

        return True


class AgaveFilesImportDataFromAgave(AgavePyWrapper):
    """
    Wraps AgavePy import data files operation for Agave-to-Agave imports.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveFilesImportDataFromAgave class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class Instance.

        """
        super(AgaveFilesImportDataFromAgave, self).__init__(
            agave,
            config,
            retry=config['import_retry'],
            retry_delay=config['import_retry_delay']
        )


    def _call(self, systemId, filePath, fileName, urlToIngest):
        """
        Wrap agavePy import data file command.

        Args:
            self: class instance
            systemId: Identifier for Agave storage system
            filePath: Path where file is to be imported
            fileName: Name of the imported file
            urlToIngest: Agave URL to be ingested

        Returns:
            True

        """
        response = self._agave.files.importData(
            systemId=systemId,
            filePath=filePath,
            fileName=fileName,
            urlToIngest=urllib.parse.quote(str(urlToIngest or ''), safe='/:')
        )
        async_response = AgaveAsyncResponse(self._agave, response)
        status = async_response.result()
        Log.some().debug(
            'import %s: %s -> agave://%s/%s/%s',
            str(status),
            urlToIngest,
            systemId,
            filePath,
            fileName
        )
        if str(status) == 'FINISHED':
            return True

        # not finished, try again
        raise Exception('agave import failed')


class AgaveJobsGetStatus(AgavePyWrapper):
    """
    Wraps AgavePy job status check operation.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveJobsGetStatus class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            False

        """
        super(AgaveJobsGetStatus, self).__init__(
            agave,
            config,
            retry=1,
            retry_delay=0
        )


    def _call(self, jobId):
        """
        Wrap agavePy job status command.

        Args:
            self: class instance
            jobId: job identifer

        Returns:
            job status

        """
        status = self._agave.jobs.getStatus(jobId=jobId)['status']

        return status


class AgaveJobsGetHistory(AgavePyWrapper):
    """
    Wraps AgavePy job history retrieval operation.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveJobsGetHistory class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
               config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class instance.

        """
        super(AgaveJobsGetHistory, self).__init__(
            agave,
            config,
            retry=1,
            retry_delay=0
        )


    def _call(self, jobId):
        """
        Wrap agavePy job history command.

        Args:
            self: class instance
            jobId: job identifer

        Returns:
            job history

        """
        response = self._agave.jobs.getHistory(
            jobId=jobId
        )

        return response


class AgaveAppsAddUpdate(AgavePyWrapper):
    """
    Wraps AgavePy apps add-update operation.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveAppsAddUpdate class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
               config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class instance.

        """
        super(AgaveAppsAddUpdate, self).__init__(
            agave,
            config,
            retry=1,
            retry_delay=0
        )

    def _call(self, body):
        """
        Wrap AgavePy apps add-update command.

        Args:
            body: Agave app definition.

        Returns:
            Apps add update response.

        """
        response = self._agave.apps.add(
            body=body
        )

        return response


class AgaveAppsPublish(AgavePyWrapper):
    """
    Wraps AgavePy app publish operation.

    Parent Class AgavePyWrapper
    """

    def __init__(self, agave, config):
        """
        Initialize AgaveAppsPublish class.

        Args:
            self: class instance
            agave: Agave connection object returned by AgavePy
            config: the Agave subsection of the GeneFlow configuration

        Returns:
            Class instance.

        """
        super(AgaveAppsPublish, self).__init__(
            agave,
            config,
            retry=1,
            retry_delay=0
        )


    def _call(self, appId):
        """
        Wrap agavePy app publish command.

        Args:
            self: class instance
            appId: Agave app ID

        Returns:
            Publish result.

        """
        response = self._agave.apps.manage(
            appId=appId,
            body={
                'action': 'publish'
            }
        )

        return response
