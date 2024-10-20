#!/usr/bin/env python3
"""Migration of logseq notes to org-roam."""

# import os
import sys
import uuid
import subprocess
import datetime
from pathlib import Path
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


def journal_file_name(name):
    """Make proper name of the journal."""


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
    """Create new file name."""
    name = current_name.lower().replace(' ', '_')
    now = datetime.datetime.now()
    return f'{new_dir}/{now:%Y%m%d%H%M%S}-{name}.org'


def main(dir, new_dir):
    """Run main action to convert files."""
    files = {}

    # get pages
    pages_dir = Path(dir + '/pages/')
    for file in pages_dir.iterdir():
        if file.stem != 'contents':
            files[file.stem] = {}
            files[file.stem]['path'] = str(dir) + '/pages/' + file.name
            files[file.stem]['ext'] = file.suffix.replace('.', '')
            files[file.stem]['source'] = 'pages'

    # get journals
    journals_dir = Path(dir + '/journals/')
    for file in journals_dir.iterdir():
        files[file.stem] = {}
        files[file.stem]['path'] = str(dir) + '/journals/' + file.name
        files[file.stem]['ext'] = file.suffix.replace('.', '')
        files[file.stem]['source'] = 'journals'

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

    # new_dir = '/home/jan/notes-to-org/_converted'

    files_newname = {
        k: {**v, 'new_path': pages_newname(k, new_dir)}
        for k, v in files_interlink.items()
        if v['source'] == 'pages'}

    files_write = files_newname

    for k, new_file in files_write.items():
        if new_file['source'] == 'pages':
            with open(new_file['new_path'], 'w', encoding='utf-8') as file:
                file.write(new_file['content'])


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
