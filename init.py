#!/usr/bin/env python3
"""Migration of logseq notes to org-roam."""

# import os
import sys
import uuid
import subprocess
import datetime
from pathlib import Path
import os
import re


def prepare_org_roam(node_title, node_id, content):
    """Make header."""
    properties_header = f"""
    :PROPERTIES:
    :ID:       {node_id}
    :END:
    #+TITLE: {node_title}
    """
    return properties_header + content


def md_to_org(input_file):
    """Convert a logseq md file to org file using pandoc."""
    try:
        # Run the pandoc command
        result = subprocess.run(
            ['pandoc', '-f', 'markdown_mmd', '-t', 'org', input_file],
            capture_output=True,
            text=True,
            check=True
        )

        # Return the converted content
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None


def journal_name(name):
    """Make proper name of the journal."""
    name_parts = name.split('_')
    journal_date = datetime.datetime(
        int(name_parts[0]),
        int(name_parts[1]),
        int(name_parts[2]))

    return f'{journal_date:%Y-%m-%d %A}'


def md_to_org_content(content):
    """Convert a logseq md file to org file using pandoc."""
    try:
        # Run the pandoc command
        result = subprocess.run(
            ['pandoc', '-f', 'markdown_mmd', '-t', 'org'],
            capture_output=True,
            input=content,
            text=True,
            check=True
        )

        # Return the converted content
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return None


def convert_logseq_to_roam_link(content, library):
    """Replace logseq links inside content."""
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    for link in links:
        if link in library:
            content = content.replace(
                f'[[{link}]]',
                f'[[id:{library[link]}][{link}]]')
    return content


def add_content(entry):
    """Get file content."""
    # file.read()
    return {**entry,
            'content': open(entry['path'], 'r', encoding='utf-8').read()}


def pages_newname(current_name, new_dir):
    """Create new file name for pages."""
    name = current_name.lower().replace(' ', '_')
    now = datetime.datetime.now()
    return f'{new_dir}/{now:%Y%m%d%H%M%S}-{name}.org'


def journals_newname(current_name, new_dir):
    """Create new file name for journal."""
    name = str(current_name)[:11]
    return f'{new_dir}/{name}.org'


def main(dir):
    """Run main action to convert files."""
    write_time = datetime.datetime.now()
    write_dir = f'{dir}-{write_time:%Y%m%d%H%M%s}'
    files = {}

    # get pages
    pages_dir = Path(dir + '/pages/')
    for file in pages_dir.iterdir():
        name = file.stem
        if name != 'contents':
            files[name] = {}
            files[name]['path'] = str(dir) + '/pages/' + file.name
            files[name]['ext'] = file.suffix.replace('.', '')
            files[name]['source'] = 'pages'

    # get journals
    journals_dir = Path(dir + '/journals/')
    for file in journals_dir.iterdir():
        name = file.stem
        files[name] = {}
        files[name]['path'] = str(dir) + '/journals/' + file.name
        files[name]['ext'] = file.suffix.replace('.', '')
        files[name]['source'] = 'journals'

    files_uuid = {
        k: {**v, 'id': str(uuid.uuid4())}
        for k, v in files.items()}

    files_content = {
        k: add_content(v)
        for k, v in files_uuid.items()}

    files_org_content = {
        k: {**v, 'content': md_to_org_content(v['content'])}
        for k, v in files_content.items()
        if v['ext'] == 'md'}

    files_header = {
        k: {**v, 'content': prepare_org_roam(k, v['id'], v['content'])}
        for k, v in files_org_content.items()}

    library = {key: value['id'] for key, value in files_uuid.items()}

    files_interlink = {
        k: {**v, 'content': convert_logseq_to_roam_link(v['content'], library)}
        for k, v in files_header.items()}

    page_newname = {
        k: {**v, 'new_path': pages_newname(k, write_dir)}
        for k, v in files_interlink.items()
        if v['source'] == 'pages'}

    journal_newname = {
        k: {**v, 'new_path': journals_newname(k, write_dir + '/journals/')}
        for k, v in page_newname.items()
        if v['source'] == 'journals'}

    files_write = journal_newname

    os.mkdir(write_dir)
    os.mkdir(write_dir + '/journals/')

    for k, new_file in files_write.items():
        if new_file['source'] == 'pages':
            with open(new_file['new_path'], 'w', encoding='utf-8') as file:
                file.write(new_file['content'])

    return write_dir


if __name__ == '__main__':
    main(sys.argv[1])


# assistencni sluzba gorenje
# 800 105 505
# electro solid
# 603 450 444
