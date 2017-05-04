from remote_host_command.public import RemoteHostCommand


class RemoteFileEditor():
    """
    takes care of editing a RemoteHosts files
    """
    _READ_FILE = RemoteHostCommand('sudo cat {FILE}')
    _WRITE_FILE = RemoteHostCommand('sudo bash -c "echo -e \\"{FILE_CONTENT}\\" > {FILE}"')
    _APPEND_FILE = RemoteHostCommand('sudo bash -c "echo -e \\"{FILE_CONTENT}\\" >> {FILE}"')
    
    def __init__(self, remote_executor):
        """
        is initialized with the remote executor the files are edited with
        
        :param remote_executor: remote executor the files are edited with
        :type remote_executor: remote_execution.public.RemoteHostExecutor
        """
        self.remote_executor = remote_executor

    def edit(self, file, text_to_replace, text_to_replace_with):
        """
        replaces a given string in a file by another one
        
        :param file: the file which will be edited
        :type file: str
        :param text_to_replace: the text to replace
        :type text_to_replace: str
        :param text_to_replace_with: the text to replace the text with
        :type text_to_replace_with: str
        """
        self.write(
            file,
            self.remote_executor.execute(
                self._READ_FILE.render(file=file)
            ).replace(text_to_replace, text_to_replace_with),
        )

    def append(self, file, text_to_append):
        """
        append something to the given file
        
        :param file: the file which will be edited
        :type file: str
        :param text_to_append: the text to append
        :type text_to_append: str
        """
        self.remote_executor.execute(
            self._APPEND_FILE.render(file=file, file_content=text_to_append)
        )

    def write(self, file, text_to_write):
        """
        Writes a file. Current content will be overwritten
        
        :param file: the file which will be edited
        :type file: str
        :param text_to_write: the text to replace
        :type text_to_write: str 
        """
        self.remote_executor.execute(
            self._WRITE_FILE.render(file=file, file_content=text_to_write)
        )
