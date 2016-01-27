# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir)))
import re
import json
import traceback
from datetime import datetime
from os.path import expanduser

if sys.version < '3':
    import commands as process
else:
    import subprocess as process

DEFAULT_SETTINGS_NAME = "FileHeader.default"
CURDIR = os.path.abspath(os.path.join(__file__, os.path.pardir))
DEFAULT_SETTINGS_PATH = os.path.join(CURDIR, "etc", DEFAULT_SETTINGS_NAME)
HEADER_PATH = os.path.join(CURDIR, 'template/header')
BODY_PATH = os.path.join(CURDIR, 'template/body')


def Settings():
    '''Get settings'''
    USER_SETTINGS_PATH = os.path.join(expanduser("~"), ".TerminalHeader", "FileHeader.user")
    with open(USER_SETTINGS_PATH) as filereader:
        contents = filereader.read()
    contents = re.subn("\s+//.*", "", contents)
    contents = re.subn("/\*[\d\D]*?\*/", "", contents[0])
    return json.loads(contents[0])


def is_hidden(path):
    '''Whether the file or dir is hidden'''

    hidden = False
    platform = sys.platform
    if platform.startswith("win"):
        status, output = process.getstatusoutput('attrib %s' % path)
        if status == 0:
            try:
                if output[4].upper() == 'H':
                    hidden = True
            except:
                pass
    else:
        basename = os.path.basename(path)
        if basename.startswith('.'):
            hidden = True
    return hidden


def can_add(path):
    '''Whether can add header to path'''

    def can_add_to_dir(path):
        return enable_add_to_hidden_dir or (not enable_add_to_hidden_dir
                                            and not is_hidden(path))

    if not os.path.exists(path):
        return False

    enable_add_to_hidden_dir = Settings().get(
        'enable_add_header_to_hidden_dir')
    enable_add_to_hidden_file = Settings().get(
        'enable_add_header_to_hidden_file')

    if os.path.isfile(path):
        if can_add_to_dir(os.path.dirname(path)):
            if enable_add_to_hidden_file or (not enable_add_to_hidden_file
                                             and not is_hidden(path)):
                return True

    elif os.path.isdir(path):
        return can_add_to_dir(path)

    return False


def get_syntax_type(name):
    '''Judge `syntax_type` according to to `name`'''

    syntax_type = Settings().get('syntax_when_not_match')
    file_suffix_mapping = Settings().get('file_suffix_mapping')
    extension_equivalence = Settings().get('extension_equivalence')

    if name is not None:
        name = name.split('.')
        if len(name) <= 1:
            return syntax_type

        for i in range(1, len(name)):
            suffix = '.'.join(name[i:])
            if suffix in extension_equivalence:
                suffix = extension_equivalence[suffix]
                break
        else:
            suffix = name[-1]

        try:
            syntax_type = file_suffix_mapping[suffix]
        except KeyError:
            pass

    return syntax_type


def get_template_part(syntax_type, part):
    '''Get template header or body'''

    tmpl_name = '%s.tmpl' % syntax_type
    path = HEADER_PATH if part == 'header' else BODY_PATH
    tmpl_file = os.path.join(path, tmpl_name)

    custom_template_path = Settings().get('custom_template_%s_path' % part)
    if custom_template_path:
        _ = os.path.join(custom_template_path, tmpl_name)
        if os.path.exists(_) and os.path.isfile(_):
            tmpl_file = _

    try:
        template_file = open(tmpl_file, 'r')
        contents = template_file.read()
        template_file.close()
    except:
        contents = ''
    return contents


def get_strftime():
    '''Get `time_format` setting'''

    _ = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%H:%M:%S']

    format = Settings().get('custom_time_format')

    if not format:
        try:
            format = _[Settings().get('time_format')]
        except IndexError:
            format = _[0]

    return format


def get_args(syntax_type, options={}):
    '''Get the args rendered.

    :Para:
        - `syntax_type`: Language type
        - `which`: candidates are 'new' and 'add'
    '''
    args = Settings().get('Default')
    args.update(Settings().get(syntax_type, {}))
    #
    format = get_strftime()

    args.update({
        'create_time': datetime.now().strftime(format),
        'last_modified_time': datetime.now().strftime(format),
    })

    if 'author' not in args:
        args.update({'author': "please add author in settings file"})
    if 'last_modified_by' not in args:
        args.update({'last_modified_by': args["author"]})
    return args


def render_template(syntax_type, part=None, options={}):
    '''Render the template correspond `syntax_type`'''

    from jinja2 import Template
    try:
        if part is not None:
            template = Template(get_template_part(syntax_type, part))
        else:
            template = Template(get_template(syntax_type))

        render_string = template.render(get_args(syntax_type, options))
    except:
        render_string = ''
        traceback.print_exc()
    return render_string


def addheader(filepath, options):
    syntax_type = get_syntax_type(filepath)
    for option in options:
        header = render_template(syntax_type, option, {'path': filepath})
        if header in ["", None]:
            return
        # new file or add header in exists file
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(header)
        else:
            with open(filepath, 'r') as f:
                if option == 'header':
                    contents = header + f.read().replace(r'\r', '')
                elif option == 'body':
                    contents = f.read().replace(r'\r', '') + header
            with open(filepath, 'w') as f:
                f.write(contents)


# 整个文件夹添加header
def addheaderinfolder(dirpath, options=('header',)):
    for root, subdirs, files in os.walk(dirpath):
        for f in files:
            file_name = os.path.join(root, f)
            if can_add(file_name):
                addheader(file_name, options)


def doinit():
    homedir = expanduser("~")
    if not os.path.exists(os.path.join(homedir, ".TerminalHeader")):
        os.mkdir(os.path.join(homedir, ".TerminalHeader"))
    if not os.path.exists(os.path.join(homedir, ".TerminalHeader", "FileHeader.user")):
        with open(DEFAULT_SETTINGS_PATH) as filereader:
            contents = filereader.read()
            with open(os.path.join(homedir, ".TerminalHeader", "FileHeader.user"), "w") as filewriter:
                filewriter.write(contents)


def main():
    # 检测是否初始化
    doinit()
    options = ('header',)
    if sys.argv[1].startswith('-'):
        option = sys.argv[1][1]
        if option == 'h':
            options = ('header',)
        elif option == 'b':
            options = ('body',)
        elif option == 'a':
            options = ('header', 'body')
        filepath = sys.argv[2]
    else:
        filepath = sys.argv[1]
    filepath = os.path.abspath(filepath)
    if os.path.isdir(filepath):
        addheaderinfolder(filepath, options)
    else:
        addheader(filepath, options)

if __name__ == '__main__':
    main()
