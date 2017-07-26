import errno
import os
import re
import shutil
import chardet
import lexos.helpers.constants as constants
import lexos.managers as managers


def get_encoding(input_string: str) -> str:
    """Uses chardet to return the encoding type of a string.
    
    :param input_string: A string.
    :return: The string's encoding type.
    """
    encoding_detect = chardet.detect(input_string[:constants.MIN_ENCODING_DETECT])
    encoding_type = encoding_detect['encoding']
    return encoding_type


def make_preview_from(input_string: str) -> str:
    """Creates a formatted preview string from a file contents string.

    :param input_string: A string from which to create the formatted preview.
    :return: The formatted preview string.
    """
    if len(input_string) <= constants.PREVIEW_SIZE:
        preview_string = input_string
    else:
        newline = '\n'
        half_length = constants.PREVIEW_SIZE // 2
        preview_string = input_string[:half_length] + '\u2026 ' + newline + \
            newline + '\u2026' + input_string[-half_length:]  # New look
    return preview_string


def generate_d3_object(word_counts: dict, object_label: str, word_label: str, count_label: str) -> object:
    """Generates a properly formatted JSON object for d3 use.
    
    :param word_counts: dictionary of words and their count
    :param object_label: The label to identify this object.
    :param word_label: A label to identify all "words".
    :param count_label: A label to identify all counts.
    :return: The formatted JSON object.
    """
    json_object = {'name': str(object_label), 'children': []}

    for word, count in list(word_counts.items()):
        json_object['children'].append({word_label: word, count_label: count})
    return json_object


def int_key(key) -> tuple:
    """Returns the key to sort by.

    :param key: A key
    :return: A key converted into an int if applicable
    """
    if isinstance(key, tuple):
        key_int = key[0]
    return tuple(int(part) if re.match(r'[0-9]+$', part) else part
                 for part in re.split(r'([0-9]+)', key_int))


def natsort(input_list: list) -> list:
    """Sorts lists in human order (10 comes after 2, even when both are strings)

    :param input_list: An unsorted list
    :return: A sorted list
    """
    return sorted(input_list, key=int_key)


def zip_dir(path: str, ziph: object):
    """zip all the file in path into a zipfile type ziph
    
    :param path: The directory that you want to zip
    :param ziph: the zipfile that you want to put the zip information in.
    """
    cur_dir = os.getcwd()  # record current path
    os.chdir(path)  # go to the path that need to be zipped
    # ziph is zipfile handle
    for root, dirs, files in os.walk(".", topdown=False):
        for file in files:
            ziph.write(os.path.join(root, file))
    os.chdir(cur_dir)  # go back to the original path


def copy_dir(src: str, dst: str):
    """copy all the file from src directory to dst directory
    
    :param src: the source dir
    :param dst: the destination dir
    """
    try:
        shutil.copytree(src, dst)
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise


def merge_list(word_lists: list) -> dict:
    """this function merges all the word_list(dictionary)

    :param word_lists: an array contain all the word_list(dictionary type)
    :return: the merged word list (dictionary type)
    """
    merged_list = {}
    for word_list in word_lists:
        for key in list(word_list.keys()):
            try:
                merged_list[key] += word_list[key]
            except KeyError:
                merged_list.update({key: word_list[key]})
    return merged_list


def load_stastic(file: str) -> dict:
    """this method takes an ALREADY SCRUBBED chunk of file(string), and convert
    that into a WordLists(see :return for this function or see the document for 
    'test' function)

    :param file: a string contain an AlREADY SCRUBBED file
    :return: a WordLists: Array type
            each element of array represent a chunk, and it is a dictionary
            type
            each element in the dictionary maps word inside that chunk to its
            frequency
    """
    words = file.split()
    word_list = {}
    for word in words:
        try:
            word_list[word] += 1
        except KeyError:
            word_list.update({word: 1})
    return word_list


def matrix_to_dict(matrix: list) -> list:
    """convert a word matrix(which is generated in getMatirx() method in
    ModelClass.py) to the one that is used in the test() method in this file.

    :param matrix: the count matrix generated by getMatrix method
    :return: a Result Array(each element is a dict) that test method can use
    """
    result_array = []
    for i in range(1, len(matrix)):
        result_dict = {}
        for j in range(1, len(matrix[0])):
            if matrix[i][j] != 0:
                result_dict.update({matrix[0][j]: matrix[i][j]})
        result_array.append(result_dict)
    return result_array


def dict_to_matrix(word_lists: list) -> tuple:
    """convert a dictionary into a DTM
    
    :param word_lists: a list of dictionaries that maps a word to word count
    each element represent a segment of the whole corpus
    :return: a dtm the first row is the word and the first column is the index 
    of this dict in the original WordLists
    """
    total_list = merge_list(word_lists)
    words = list(total_list.keys())
    matrix = [[''] + words]
    word_list_num = 0
    for word_list in word_lists:
        row = [word_list_num]
        for key in list(total_list.keys()):
            try:
                row.append(word_list[key])
            except KeyError:
                row.append(0)
        matrix.append(row)
        word_list_num += 1
    return matrix, words


def xml_handling_options(data=None):
    """
    
    :param data: 
    """
    file_manager = managers.utility.loadFileManager()
    from lexos.managers import session_manager
    text = ""
    # BeautifulSoup to get all the tags
    for file in file_manager.get_active_files():
        text = text + " " + file.load_contents()
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
            session_manager.session['xmlhandlingoptions'][tag] = {
                "action": 'remove-tag', "attribute": ''}
    if data:
        # If they have saved, data is passed.
        # This block updates any previous entries in the dict
        # that have been saved
        for key in list(data.keys()):
            if key in tags:
                data_values = data[key].split(',')
                session_manager.session['xmlhandlingoptions'][key] = \
                    {
                        "action": data_values[0],
                        "attribute": data["attributeValue" + key]
                    }
    for key in list(session_manager.session['xmlhandlingoptions'].keys()):
        # makes sure that all current tags are in the active docs
        if key not in tags:
            del session_manager.session['xmlhandlingoptions'][key]


def html_escape(text: str) -> str:
    """escape all the html content
    
    :param text: the input string
    :return: the string with all the html syntax escaped so that it will be 
    safe to put the returned string to html
    """
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def apply_function_exclude_tags(text: str, functions: list) -> str:
    """strips the given text
    
    :param text: string to strip
    :param functions: a list of functions
    :return: striped text
    """
    # type: (str, list) -> str
    striped_text = ''
    tag_pattern = re.compile(r'<.+?>', re.UNICODE | re.MULTILINE)
    tags = re.findall(tag_pattern, text)
    contents = re.split(tag_pattern, text)
    for i in range(len(tags)):
        for function_to_apply in functions:
            contents[i] = function_to_apply(contents[i])
        striped_text += contents[i]
        striped_text += tags[i]
    for function_to_apply in functions:
        contents[-1] = function_to_apply(contents[-1])
    striped_text += contents[-1]
    return striped_text


def decode_bytes(raw_bytes: str) -> str:
    """decode the raw bytes, typically used to decode `request.file`
    :param raw_bytes: the bytes you get and want to decode to string
    :return: A decoded string
    """
    try:
        # try to use utf-8 to decode first
        encoding_type = "utf-8"
        # Grab the file contents, which were encoded/decoded automatically into
        # python's format
        decoded_string = raw_bytes.decode(encoding_type)
    except UnicodeDecodeError:
        encoding_detect = chardet.detect(
            raw_bytes[:constants.MIN_ENCODING_DETECT])  # Detect the encoding
        encoding_type = encoding_detect['encoding']
        # Grab the file contents, which were encoded/decoded automatically into
        # python's format
        decoded_string = raw_bytes.decode(encoding_type)
    return decoded_string
