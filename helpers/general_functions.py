import os
import re
import shutil
import errno
import helpers.constants as constants
import managers

# import base64
# from Crypto.Cipher import DES3
# from Crypto.Hash import MD5
# from Crypto import Random




def makePreviewFrom(string):
    """
    Creates a formatted preview string from a file contents string.

    Args:
        string: A string from which to create the formatted preview.

    Returns:
        The formatted preview string.
    """
    if len(string) <= constants.PREVIEW_SIZE:
        previewString = string
    else:
        newline = '\n'
        halfLength = constants.PREVIEW_SIZE // 2
        previewString = string[:halfLength] + u'\u2026 ' + newline + newline + u'\u2026' + string[
                                                                                           -halfLength:]  # New look
    #previewString = string
    return previewString


def generateD3Object(wordCounts, objectLabel, wordLabel, countLabel):
    """
    Generates a properly formatted JSON object for d3 use.

    Args:
        objectLabel: The label to identify this object.
        wordLabel: A label to identify all "words".
        countLabel: A label to identify all counts.

    Returns:
        The formatted JSON object.
    """
    JSONObject = {}

    JSONObject['name'] = str(objectLabel.encode('utf-8'))

    JSONObject['children'] = []

    for word, count in wordCounts.items():
        JSONObject['children'].append({wordLabel: word.encode('utf-8'), countLabel: count})

    return JSONObject


def intkey(s):
    """
    Returns the key to sort by.

    Args:
        A key

    Returns:
        A key converted into an int if applicable
    """
    if type(s) == tuple:
        s = s[0]
    return tuple(int(part) if re.match(r'[0-9]+$', part) else part
                 for part in re.split(r'([0-9]+)', s))


def natsort(l):
    """
    Sorts lists in human order (10 comes after 2, even when both are strings)

    Args:
        A list

    Returns:
        A sorted list
    """
    return sorted(l, key=intkey)


def zipdir(path, ziph):
    """
    zip all the file in path into a zipfile type ziph
    :param path: a dir that you want to zip
    :param ziph: the zipfile that you want to put the zip information in.
    """
    cur_dir = os.getcwd()  # record current path
    os.chdir(path)  # go to the path that need to be zipped
    # ziph is zipfile handle
    for root, dirs, files in os.walk(".", topdown=False):
        for file in files:
            ziph.write(os.path.join(root, file))
    os.chdir(cur_dir)  # go back to the original path


def copydir(src, dst):
    """
    copy all the file from src directory to dst directory
    :param src: the source dir
    :param dst: the destination dir
    :raise:
    """
    try:
        shutil.copytree(src, dst)
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise


def merge_list(wordlists):
    """
    this function merges all the wordlist(dictionary) into one, and return it

    :param wordlists: an array contain all the wordlist(dictionary type)
    :return: the merged word list (dictionary type)
    """
    mergelist = {}
    for wordlist in wordlists:
        for key in wordlist.keys():
            try:
                mergelist[key] += wordlist[key]
            except:
                mergelist.update({key: wordlist[key]})
    return mergelist


def loadstastic(file):
    """
    this method takes an ALREADY SCRUBBED chunk of file(string), and convert that into a WordLists
    (see :return for this function or see the document for 'test' function, :param WordLists)

    :param file: a string contain an AlREADY SCRUBBED file
    :return: a WordLists: Array type
            each element of array represent a chunk, and it is a dictionary type
            each element in the dictionary maps word inside that chunk to its frequency
    """
    Words = file.split()
    Wordlist = {}
    for word in Words:
        try:
            Wordlist[word] += 1
        except:
            Wordlist.update({word: 1})
    return Wordlist


def matrixtodict(matrix):
    """
    convert a word matrix(which is generated in getMatirx() method in ModelClass.py) to
    the one that is used in the test() method in this file.

    :param matrix: the count matrix generated by getMatrix method
    :return: a Result Array(each element is a dict) that test method can use
    """
    ResultArray = []
    for i in range(1, len(matrix)):
        ResultDict = {}
        for j in range(1, len(matrix[0])):
            if matrix[i][j] != 0:
                ResultDict.update({matrix[0][j]: matrix[i][j]})
        ResultArray.append(ResultDict)
    return ResultArray


def dicttomatrix(WordLists):
    """
    convert a dictionary into a DTM
    :param WordLists: a list of dictionaries that maps a word to word count
                        each element represent a segment of the whole corpus
    :return:
        a dtm the first row is the word and the first column is the index of this dict in the original WordLists
    """
    Totallist = merge_list(WordLists)
    Words = Totallist.keys()
    Matrix = [[''] + Words]
    wordlistnum = 0
    for wordlist in WordLists:
        row = [wordlistnum]
        for key in Totallist.keys():
            try:
                row.append(wordlist[key])
            except KeyError:
                row.append(0)
        Matrix.append(row)
        wordlistnum += 1

    return Matrix, Words

def xmlHandlingOptions(data=0):
    fileManager = managers.utility.loadFileManager()
    from managers import session_manager
    text = ""
    #BeautifulSoup to get all the tags
    for file in fileManager.getActiveFiles():
        text = text + " " + file.loadContents()
    import bs4
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(text, 'html.parser')
    for e in soup:
        if isinstance(e, bs4.element.ProcessingInstruction):
            e.extract()

    tags = []
    [tags.append(tag.name) for tag in soup.find_all()]
    tags = list(set(tags))
    from natsort import humansorted
    tags = humansorted(tags)

    for tag in tags:
        if tag not in session_manager.session['xmlhandlingoptions']:
            session_manager.session['xmlhandlingoptions'][tag] = {"action": 'remove-tag',"attribute": ''}

    if data:    #If they have saved, data is passed. This block updates any previous entries in the dict that have been saved
        for key in data.keys():
            if key in tags:
                dataValues = data[key].split(',')
                session_manager.session['xmlhandlingoptions'][key] = {"action": dataValues[0], "attribute": data["attributeValue"+key]}

    for key in session_manager.session['xmlhandlingoptions'].keys():
        if key not in tags: #makes sure that all current tags are in the active docs
            del session_manager.session['xmlhandlingoptions'][key]


# def encryptFile(path, key):
#     """
#     encrypt a file on path using the key (DES encryption)
#     :param path: the path of the file you want to encrypt (this encrypt file will deleted)
#     :param key: the key you use to encrypt you file
#     """
#     # read content from a file
#     f = open(path, 'rb')
#     message = f.read()
#     f.close()
#
#     # generate a random initialize vector
#     initVector = Random.new()
#     initVector = initVector.read(DES3.block_size)
#     key = MD5.new(key).digest()
#
#     # because DES can only encrypt message with multiple of 8, not encrypt the first couple of the letter
#     letterKeep = message[:len(message) % 8]
#     message = message[len(message) % 8:]
#
#     # generate a encryption object and encrypt the message
#     encryption = DES3.new(key, DES3.MODE_OFB, initVector)
#     cipher = encryption.encrypt(message)
#
#     # write the encrypt message that into the file
#     f = open(path, 'wb')
#     f.write(base64.b64encode(initVector + '\n' + letterKeep + '\n' + cipher))
#     f.close()
#
#
# def decryptFile(path, key):
#     """
#     decrypt a file on path using the key (DES encryption)
#     :param path: the path of the file you want to decrypt (this encrypt file will deleted)
#     :param key: the key you use to encrypt you file
#     :return: the path that the plain text is stored *MAKE SURE THAT YOU DELETE THAT AFTER USE*
#     """
#     # read content from a file
#     f = open(path, 'rb')
#     content = base64.b64decode(f.read())
#     print content
#     content = content.split('\n', 2)
#     f.close()
#
#     # read the initVector and cipher, and letterKeep
#     initVector = content[0]
#     letterKeep = content[1]
#     cipher = content[2]
#     key = MD5.new(key).digest()
#
#     # generate a encryption object and decrypt the message
#     encryption = DES3.new(key, DES3.MODE_OFB, initVector)
#     message = encryption.decrypt(cipher)
#
#     # write the encrypt message that into the file
#     f = open(path + 'plain_text', 'wb')
#     f.write(letterKeep + message)
#     f.close()
#
#     # *MAKE SURE THAT YOU DELETE THIS PATH AFTER USE*
#     return path + 'plain_text'

