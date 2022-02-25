class File:
    """
    Class to represent a file within the OS
    """
    def __init__(self, name: str = "", contents: str = "") -> None:
        """
        Basic constructor for a file

        :param name: Name of file
        :param contents: Contents of the file
        """
        self.name = name
        self.contents = contents # Contains a string of the file

    def append(self, text: str = "") -> None:
        """
        Append something to the file

        :param text: Text to append
        :return: None
        """
        self.contents += text

    def write(self, text: str = "") -> None:
        """
        Overwrites the file's text

        :param text: Text to overwrite with
        :return: None
        """
        self.contents = text

    def read(self) -> str:
        """
        Read the text from the file

        :return: None
        """
        return self.contents

    def copy_from(self, dir, name: str = "") -> None:
        """
        Copies everything

        :param dir: From copy
        :param name: New name
        :return: None
        """
        if not name:
            self.name = dir.name
        else:
            self.name = name
        self.contents = dir.contents

