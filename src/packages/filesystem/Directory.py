import copy

from ..resources.colors import colors
from ..resources import variables as var
from .File import File

class Directory:
    """
    Class to represent a folder in the filesystem
    """
    def __init__(self, name="", container=None):
        """
        Constructor for a basic folder

        :param name: Name of the folder
        :param container: Containing folder
        """
        self.name = name
        self.contents = []
        self.container = container

    def index(self, find):
        """
        Gets the index of the folder by its name

        :param find: Name of folder to find
        :return: Index of folder
        """
        for i in range(len(self.contents)):
            if self.contents[i].name == find:
                return i
        return -1

    def add(self, dirFile):
        """
        Add a file or directory to the container

        :param dirFile: Directory or File to add
        :return: Whether it was successful or not
        """
        # Check for duplicate names
        if self.index(dirFile.name) != -1:
            return False

        self.contents.append(dirFile)
        return True

    def get(self, neededName):
        """
        Get a folder or file from the current directory

        :param neededName: Name of folder/file to grab
        :return: Reference to the searched name
        """
        ind = self.index(neededName)
        if ind >= 0:
            return self.contents[ind]

    def has_sub(self):
        """
        Does this directory have at least one sub directory?

        :return: If it has sub or not
        """
        for content in self.contents:
            if type(content) == Directory:
                return True
        return False

    def get_sub(self, path=""):
        """
        Iterates through the path recursively looking for slashes

        :param path: Path to search through
        :return: Reference to the desired dir or file
        """
        if path == "":
            return self
        
        pathSplit = path.split("/")
        nextDir = self.index(pathSplit[0])

        # Check if it's ../
        if pathSplit[0] == "..":
            pathSplit.pop(0)
            path = "/".join(pathSplit)
            if self.container == None:
                return self.get_sub(path)
            else:
                return self.container.get_sub(path)
        
        # Check if it's ./
        if pathSplit[0] == ".":
            pathSplit.pop(0)
            path = "/".join(pathSplit)
            return self.get_sub(path)

        if nextDir < 0:
            return False
        
        pathSplit.pop(0)
        path = "/".join(pathSplit)

        if nextDir >= 0:
            if type(self.contents[nextDir]) == File:
                return self.contents[nextDir]
            return self.contents[nextDir].get_sub(path)

    def get_path(self):
        """
        Gets path to current directory

        :return: String of path to current directory
        """
        if self.container == None:
            return self.name
        
        return self.container.get_path() + "/" + self.name

    def get_container(self, path=""):
        """
        Gets the container of this directory

        :param path: Path to look for
        :return: Reference to the searched for item
        """
        toR = self.get_sub("/".join(path.split("/")[:-1]))
        if toR == False:
            return self
        return toR

    def delete(self, path=""):
        """
        Delete a file or directory by name

        :param path: Path to delete
        :return: Whether it was successful
        """
        ind = -1
        if path:
            pathSplit = path.split("/")
            if len(pathSplit) == 1:
                ind = self.index(pathSplit[0])
                if ind >= 0:
                    self.contents.pop(ind)
                    return True


            name = pathSplit.pop()
            path = "/".join(pathSplit)
            ind = self.get_sub(path).index(name)
            if ind >= 0:
                self.get_sub(path).contents.pop(ind)
                return True
        return False

    def copy_from(self, dir, name=""):
        """
        Perform a copy from a dir to a new directory

        :param dir: Directory to copy
        :param name: Name of the directory to copy
        :return: None
        """
        if not name:
            self.name = dir.name
        else:
            self.name = name
        self.contents = dir.contents

    # ============== Shell Commands ==============

    def ls(self, path=""):
        """
        List all contents of the directory

        :param path: Path to list
        :return: Whether it was successful
        """
        if not self.get_sub(path):
            print("ls: cannot access '{}': No such file or directory".format(path))
            return False
        destContents = self.get_sub(path).contents

        lenContent = len(self.get_sub(path).contents)

        for content in destContents:
            if type(content) == Directory:
                if var.colorPrompt:
                    print(colors.fg.blue + content.name + colors.reset + "\t", end="")
                else:
                    print(content.name + "\t", end="")
            else:
                print(content.name + "\t", end="")
        if lenContent != 0:
            print()

    def mkdir(self, path=""):
        """
        Make a new directory

        :param path: Path to create
        :return: Whether it was successful
        """
        if path:
            # Check if the name already exists
            if self.get_sub(path):
                print("mkdir: cannot create directory '{}': File exists".format(path))
                return False
            pathSplit = path.split("/")
            if len(pathSplit) == 1:
                self.add(Directory(pathSplit[0], self))
                return True

            name = pathSplit.pop()
            path = "/".join(pathSplit)
            self.get_sub(path).add(Directory(name, self.get_sub(path)))
            return True
        return False

    def mv(self, orig="", final=""):
        """
        Rename or move anything

        :param orig: Original
        :param final: Destination
        :return: Whether it was successful
        """
        # Print error for no operands
        if not orig and not final:
            print("mv: missing file operand")
            var.exit_code = 1
            return False
        # Print error for one arg
        if not final:
            print("mv: missing destination file operand after '{}'".format(orig))
            var.exit_code = 1
            return False
        
        if not self.get_sub(orig):
            print("mv: cannot stat '{}': No such file or directory".format(orig))
            var.exit_code = 1
            return False

        # Check if destination is a file exists
        if self.get_sub(final) and type(self.get_sub(final)) == File:
            print("mv: destination exists")
            var.exit_code = 1
            return False
        
        # Move file by copying and deleting old
        if self.cp(orig, final, True, True):
            self.get_container(orig).delete(orig.split("/")[-1])
        var.exit_code = 0
        return True

    def cp(self, orig="", final="", recurse=False, fromMv=False):
        """
        Copy from to destination

        :param orig: Original to copy
        :param final: Destination to save to
        :param recurse: Whether it should recursively copy
        :param fromMv: If this was called from mv
        :return: Whether it was successful
        """
        # Make sure both are entered
        if not orig and not final:
            if not fromMv:
                print("cp: missing file operand")
            var.exit_code = 1
            return False
        
        # Check if no final is entered
        if not final:
            if not fromMv:
                print("cp: missing destination file operand after '{}'".format(orig))
            var.exit_code = 1
            return False

        # Make sure source exists
        if not self.get_sub(orig):
            if not fromMv:
                print("cp: cannot stat '{}': No such file or directory".format(orig))
            var.exit_code = 1
            return False
        
        # Check if dest exists and is a file
        if self.get_sub(final) and type(self.get_sub(final)) == File:
            if not fromMv:
                print("cp: destination exists")
            var.exit_code = 1
            return False

        # Check if recurse flag is needed
        if not fromMv and not recurse and type(self.get_sub(orig)) == Directory:
            print("cp: -r not specified; omitting directory '{}'".format(orig))
            var.exit_code = 1
            return False
        
        # Copy if source is file
        if type(self.get_sub(orig)) == File:
            dest = None
            name = ""
            # Check if dest is a folder
            if type(self.get_sub(final)) == Directory:
                dest = self.get_sub(final)
                name = self.get_sub(orig).name

                # Exit if dest exists
                if dest.index(name) >= 0:
                    var.exit_code = 1
                    return False
    
            # Check if dest doesn't exist, but container does
            elif not self.get_sub(final) and type(self.get_container(final)) == Directory:
                dest = self.get_container(final)
                name = final.split("/")[-1]

                # Exit if dest exists
                if dest.index(name) >= 0:
                    var.exit_code = 1
                    return False
            
            # Copy the file and apply the name
            if dest and name:
                copyObj = copy.deepcopy(self.get_sub(orig))
                copyObj.name = name
                dest.add(copyObj)
                var.exit_code = 0
                return True
        
        # Copy if source is folder
        elif type(self.get_sub(orig)) == Directory:
            dest = None
            name = ""

            # Print message if they're same, but continue program
            if self.get_sub(orig) == self.get_sub(final):
                if not fromMv:
                    print("cp: cannot copy a directory, '{0}', into itself, '{0}/{1}'".format(orig, final.split("/")[-1]))
                
            # Check if moving into dir
            if type(self.get_sub(final)) == Directory:
                dest = self.get_sub(final)
                name = self.get_sub(orig).name

                # Exit if dest exists
                if dest.index(name) >= 0:
                    var.exit_code = 1
                    return False

            # Check if moving and renaming
            if not self.get_sub(final) and type(self.get_container(final)) == Directory:
                dest = self.get_container(final)
                name = final.split("/")[-1]

                # Exit if dest exists
                if dest.index(name) >= 0:
                    var.exit_code = 1
                    return False
            
            # Move and set name
            if dest and name:
                copyDir = copy.deepcopy(self.get_sub(orig))
                copyDir.name = name
                copyDir.container = dest
                dest.add(copyDir)
                var.exit_code = 0
                return True
        
        return False

    def touch(self, path=""):
        """
        Make a new empty file

        :param path: Path to create
        :return: Whether it was successful
        """
        if path:
            pathSplit = path.split("/")
            if len(pathSplit) == 1:
                if self.index(pathSplit[0]) >= 0:
                    return True
                else:
                    self.add(File(pathSplit[0]))
                    return True

            name = pathSplit.pop()
            path = "/".join(pathSplit)
            self.get_sub(path).add(File(name))

    def rm(self, path="", recurse=False):
        """
        Delete a given file

        :param path: Path to delete
        :param recurse: Whether it should be deleted recursively
        :return: Whether it was successful
        """
        if path:
            if type(self.get_sub(path)) == File:
                self.delete(path)
                return True
            elif type(self.get_sub(path)) == Directory:
                if recurse:
                    self.delete(path)
                    return True
                print("rm: cannot remove '{}': Is a directory".format(path))
                return False
            else:
                print("rm: cannot remove '{}': No such file or directory".format(path))
                return False

    def rmdir(self, path=""):
        """
        Delete a directory

        :param path: Path to delete
        :return: Whether it was successful
        """
        if path:
            if type(self.get_sub(path)) == Directory:
                # Exit if empty
                if self.get_sub(path).contents:
                    print("rmdir: failed to remove '{}': Directory not empty".format(path))
                    return False
                self.delete(path)
                return True

            elif type(self.get_sub(path)) == File:
                print("rmdir: failed to remove '{}': Not a directory".format(path))
                return False
            else:
                print("rmdir: failed to remove '{}': No such file or directory".format(path))
                return False
        return False
