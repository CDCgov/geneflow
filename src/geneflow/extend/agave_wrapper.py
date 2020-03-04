"""This module contains the GeneFlow AgaveWrapper class."""

import os
import time
import urllib.parse

try:
    from agavepy.agave import Agave
    from agavepy.asynchronous import AgaveAsyncResponse
except ImportError: pass

from geneflow.log import Log


class AgaveWrapper:
    """
    Agave wrapper class.

    Wraps the Agavepy python module and adds retry and token refresh
    functionality via a decorator class.

    """

    class AgaveRetry:
        """
        Agave Retry Decorator class.

        Adds retry and token refresh functionality to all decorated Agave
        calls.

        """

        def __init__(self, func_key, silent_404=False):
            """
            Initialize decorator class

            Args:
                self: instance of decorator class.
                func_key: descriptor for function to be decorated. This is used
                    to look up the retry # and retry delay times.
                silent_404: whether to suppress warning messages for 404 errors

            """
            self._func_key = func_key
            self._silent_404 = silent_404

        def __call__(self, func):
            """

            """
            def wrapped_func(that, *args, **kwargs):
                """
                Wrap function for executing an AgavePy command.

                Args:
                    that: AgaveWrapper class instance.
                    *args: Any arguments to be sent to the AgavePy command.
                    **kwargs: Any keyword-value arguments to be sent to the
                        AgavePy command.

                Returns:
                    result of the AgavePy command call.

                """
                num_tries = 0
                num_token_tries = 0
                retry = that._config.get(
                    self._func_key+'_retry',
                    that._config['retry']
                )
                retry_delay = that._config.get(
                    self._func_key+'_retry_delay',
                    that._config['retry_delay']
                )

                while (
                        num_tries < retry
                        and num_token_tries < that._config['token_retry']
                ):
                    try:
                        try:
                            result = func(that, *args, **kwargs)
                            return result

                        except Exception as err:
                            # check for expired token error
                            if str(err).startswith('401'):
                                num_token_tries += 1
                                Log.a().warning(
                                    'agave token error [%s]', str(err)
                                )
                                time.sleep(that._config['token_retry_delay'])

                                # token could not be refreshed, most likely
                                # because token was refreshed in a different
                                # thread/process

                                # create new token
                                if that._config['connection_type']\
                                        == 'impersonate':
                                    # re-init object without losing object
                                    # binding
                                    that._agave.__init__(
                                        api_server=that._config['server'],
                                        username=that._config['username'],
                                        password=that._config['password'],
                                        token_username=that._config[
                                            'token_username'
                                        ],
                                        client_name=that._config['client'],
                                        api_key=that._config['key'],
                                        api_secret=that._config['secret'],
                                        verify=False
                                    )

                                elif that._config['connection_type']\
                                        == 'agave-cli':
                                    # get updated credentials from
                                    # ~/.agave/current
                                    agave_clients = Agave._read_clients()
                                    # don't verify ssl
                                    agave_clients[0]['verify'] = False
                                    # re-init object without losing object
                                    # binding
                                    that._agave.__init__(**agave_clients[0])

                                else:
                                    # shouldn't reach this condition, but raise
                                    # exception just in case
                                    raise Exception(
                                        'invalid agave connection type: {}'\
                                            .format(
                                                that._config['connection_type']
                                            )
                                    )

                            if str(err).startswith('404'):
                                if not self._silent_404:
                                    Log.a().warning('agave file/dir/object not found [%s]', str(err))

                                # don't retry if 404 error
                                return False

                            # not a token error, re-raise
                            raise err

                    except Exception as err:
                        num_tries += 1
                        Log.a().warning('agave call failed [%s]', str(err))
                        time.sleep(retry_delay)

                if num_token_tries == that._config['token_retry']:
                    # failed after reaching token refresh attempt limit
                    Log.an().error(
                        'agave token refresh max tries (%s) exceeded',
                        that._config['token_retry']
                    )
                    return False

                if num_tries == retry:
                    # failed due to other exceptions
                    Log.an().error(
                        'agave call max tries (%s) exceeded', retry
                    )
                    return False

                return result

            return wrapped_func


    def __init__(self, config, agave=None, token_username=None):

        self._config = config
        self._agave = agave

        if token_username:
            self._config['token_username'] = token_username


    def connect(self):
        agave_connection_type = self._config.get(
            'connection_type', 'impersonate'
        )

        if agave_connection_type == 'impersonate':
            self._agave = Agave(
                api_server=self._config['server'],
                username=self._config['username'],
                password=self._config['password'],
                token_username=self._config['token_username'],
                client_name=self._config['client'],
                api_key=self._config['key'],
                api_secret=self._config['secret'],
                verify=False
            )

        elif agave_connection_type == 'agave-cli':
            # get credentials from ~/.agave/current
            agave_clients = Agave._read_clients()
            agave_clients[0]['verify'] = False # don't verify ssl
            self._agave = Agave(**agave_clients[0])
            # when using agave-cli, token_username must be the same as the
            # stored creds in user's home directory, this can be different
            # from job username
            self._config['token_username'] \
                = agave_clients[0]['username']

        else:
            Log.an().error(
                'invalid agave connection type: %s', agave_connection_type
            )
            return False

        return True


    @AgaveRetry('files_list', silent_404=True)
    def files_exist(self, system_id, file_path):
        """
        Wrap AgavePy file listing command to check if file exists.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path for file listing.

        Returns:
            True if file/dir exists.
            False if file/dir does not exist.

        """
        if self._agave.files.list(
            systemId=system_id,
            filePath=file_path
        ):
            return True

        return False


    @AgaveRetry('files_list')
    def files_list(self, system_id, file_path):
        """
        Wrap AgavePy file listing command.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path for file listing.

        Returns:
            List of file names.

        """
        files = [
            {
                'name': f.name,
                'type': f.type
            } for f in self._agave.files.list(
                systemId=system_id,
                filePath=file_path,
                limit=1000000
            ) if f.name[:1] != '.' # skip files that start with .
        ]

        return files


    def _recursive_download(self, system_id, file_path, target_path, depth):
        """
        Recursively download files from an Agave location.

        Args:
            self: class instance.
            system_id: Agave system to download from.
            file_path: Agave path of file or folder to download.
            target_path: local directory path for download target.
            depth: recursion depth: -1=all, 0=nothing, 1=file or
                directory and all files under it.

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        if depth == 0:
            # done downloading to specified depth
            return True

        files = self._agave.files.list(
            systemId=system_id,
            filePath=file_path,
            limit=1000000
        )
        for file in files:
            if file['name'] == '.':
                # create directory at target location
                os.makedirs(target_path)
                continue

            if file['type'] == 'file':
                # download file
                agave_uri = None
                local_uri = None
                if len(files) > 1:
                    agave_uri = 'agave://{}{}/{}'.format(
                        system_id, file_path, file['name']
                    )
                    local_uri = os.path.join(target_path, file['name'])

                else:
                    # toplevel target is a file
                    agave_uri = 'agave://{}{}'.format(system_id, file_path)
                    local_uri = target_path

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
                    system_id,
                    '{}/{}'.format(file_path, file['name']),
                    os.path.join(target_path, file['name']),
                    depth-1 if depth != -1 else -1
                )

        return True


    @AgaveRetry('files_download')
    def files_download(self, system_id, file_path, target_path, depth=-1):
        """
        Wraps AgavePy files download and adds recursion.

        Args:
            self: class instance.
            system_id: Agave system to download from.
            file_path: Agave path of file or folder to download.
            target_path: local directory path for download target.
            depth: recursion depth: -1=all, 0=nothing, 1=file or
                directory and all files under it.

        Returns:
            The result of the recursive download function.

        """
        return self._recursive_download(
            system_id, file_path, target_path, depth
        )


    @AgaveRetry('files_delete')
    def files_delete(self, system_id, file_path):
        """
        Wrap AgavePy file delete command.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path for file to be deleted.

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        self._agave.files.delete(
            systemId=system_id,
            filePath=file_path
        )

        return True


    @AgaveRetry('files_mkdir')
    def files_mkdir(self, system_id, file_path, dir_name):
        """
        Wrap AgavePy make directory command.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path where directory to be created.
            dir_name: Name of new directory to be created.

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        self._agave.files.manage(
            systemId=system_id,
            filePath=file_path,
            body={
                'action': 'mkdir',
                'path': dir_name
            }
        )

        return True


    @AgaveRetry('jobs_submit')
    def jobs_submit(self, body):
        """
        Wrap AgavePy submit job command.

        Args:
            self: class instance.
            body: job template to be submitted.

        Returns:
            On success: Job descriptor object.
            On failure: Throws exception.

        """
        job = self._agave.jobs.submit(body=body)

        return job


    @AgaveRetry('files_import')
    def files_import_from_local(
        self, system_id, file_path, file_name, file_to_upload
    ):
        """
        Wrap AgavePy import data file command.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path where file is to be imported.
            file_name: Name of the imported file.
            file_to_upload: File or folder path to upload to Agave.

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        if os.path.isdir(file_to_upload):
            # create target directory, which is "file_name"
            if not self.files_mkdir(system_id, file_path, file_name):
                Log.an().error(
                    'cannot create folder at uri: agave://%s%s/%s',
                    system_id, file_path, file_name
                )
                return False


            # walk through local directory structure
            for root, dirs, files in os.walk(file_to_upload, topdown=True):
                # translate local path to dest path
                dest_file_path = os.path.join(
                    file_path, file_name, root[len(file_to_upload)+1:]
                )
                # upload each file in this directory level
                for name in files:
                    # read file in binary mode to transfer
                    response = self._agave.files.importData(
                        systemId=system_id,
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
                        system_id,
                        dest_file_path,
                        name
                    )
                    if status != 'FINISHED':
                        return False

                # create new directory for each directory in this level
                for name in dirs:
                   # create dest directory
                    if not self.files_mkdir(
                            system_id,
                            dest_file_path,
                            name
                    ):
                        Log.an().error(
                            'cannot create folder at uri: agave://%s%s/%s',
                            system_id,
                            dest_file_path,
                            name
                        )
                        return False

        elif os.path.isfile(file_to_upload):
            # import single file
            response = self._agave.files.importData(
                systemId=system_id,
                filePath=file_path,
                fileName=file_name,
                fileToUpload=open(file_to_upload, 'rb')
            )
            async_response = AgaveAsyncResponse(self._agave, response)
            status = async_response.result()
            Log.some().debug(
                'import %s: %s -> agave://%s/%s/%s',
                str(status),
                file_to_upload,
                system_id,
                file_path,
                file_name
            )
            if status != 'FINISHED':
                return False

        return True


    @AgaveRetry('files_import')
    def files_import_from_agave(
        self, system_id, file_path, file_name, url_to_ingest
    ):
        """
        Wrap AgavePy import data file command.

        Args:
            self: class instance.
            system_id: Identifier for Agave storage system.
            file_path: Path where file is to be imported.
            file_name: Name of the imported file.
            url_to_ingest: Agave URL to be ingested.

        Returns:
            On success: True with no exceptions.
            On failure: Throws exception.

        """
        response = self._agave.files.importData(
            systemId=system_id,
            filePath=file_path,
            fileName=file_name,
            urlToIngest=urllib.parse.quote(str(url_to_ingest or ''), safe='/:')
        )
        async_response = AgaveAsyncResponse(self._agave, response)
        status = async_response.result()
        Log.some().debug(
            'import %s: %s -> agave://%s/%s/%s',
            str(status),
            url_to_ingest,
            system_id,
            file_path,
            file_name
        )
        if str(status) == 'FINISHED':
            return True

        # not finished, try again
        raise Exception('agave import failed')


    @AgaveRetry('jobs_get_status')
    def jobs_get_status(self, job_id):
        """
        Wrap AgavePy job status command.

        Args:
            self: class instance.
            job_id: job identifer.

        Returns:
            On success: Job status.
            On failure: Throws exception.

        """
        status = self._agave.jobs.getStatus(jobId=job_id)['status']

        return status


    @AgaveRetry('jobs_get_history')
    def jobs_get_history(self, job_id):
        """
        Wrap agavePy job history command.

        Args:
            self: class instance.
            job_id: job identifer.

        Returns:
            On success: Job history.
            On failure: Throws exception.

        """
        response = self._agave.jobs.getHistory(
            jobId=job_id
        )

        return response


    @AgaveRetry('apps_add_update')
    def apps_add_update(self, body):
        """
        Wrap AgavePy apps add-update command.

        Args:
            body: Agave app definition.

        Returns:
            On success: Apps add update response.
            On failure: Throws exception.

        """
        response = self._agave.apps.add(
            body=body
        )

        return response


    @AgaveRetry('apps_publish')
    def apps_publish(self, app_id):
        """
        Wrap agavePy app publish command.

        Args:
            self: class instance.
            app_id: Agave app ID.

        Returns:
            On success: Publish result.
            On failure: Throws exception.

        """
        response = self._agave.apps.manage(
            appId=app_id,
            body={
                'action': 'publish'
            }
        )

        return response
