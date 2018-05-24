"""Download files from https server."""
import csv
import os
import re
from itertools import groupby

import click
import requests
from requests.auth import HTTPBasicAuth
import voluptuous as vol
from bs4 import BeautifulSoup

ARCHIVE_PATH = '/archive'


def load_csv(path):
    """Load csv file."""
    files = []
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        mysniffer = csv.Sniffer()
        has_header = mysniffer.has_header(csvfile.read(1024))
        csvfile.seek(0)
        if has_header:
           print('header found, skipping first line')
           next(reader, None)
        for row in reader:
            files.append(row[0])
    return files


def parse_page(page, root, exclude=None, include=None):
    """Parse the request text."""
    soup = BeautifulSoup(page, 'html.parser')
    file_urls = [
        os.path.join(root, node.get('href'))
        for node in soup.find_all('a')]
    if exclude:
        file_urls = [
            url for url in file_urls if not re.search(exclude, url)]
    if include:
        file_urls = [
            url for url in file_urls if re.search(include, url)]
    return file_urls


def request(url, creds, stream=False):
    """Return request from url."""
    req = requests.get(
        url, auth=HTTPBasicAuth(*creds), stream=stream, timeout=10.0)
    req.raise_for_status()
    return req


def sort_by_folder(paths):
    """Return a function that checks the paths and groups them by folder."""
    results = []

    def is_same_folder(index_path):
        """Return previous result if same folder is in previous path."""
        idx, path = index_path
        folder_name = os.path.basename(os.path.dirname(path))
        if (idx > 0 and folder_name in paths[idx - 1]):
            prev_result = results[idx - 1]
            results.append(prev_result)
            return prev_result
        elif idx > 0:
            prev_result = results[idx - 1]
            new_result = not prev_result
            results.append(new_result)
            return new_result
        result = False
        results.append(result)
        return result

    return is_same_folder


def group_by_folder(paths):
    """Return a list representing groups of paths from the same folder.

    The each item in the list will be a list of tuples. Each tuple will
    have two items, index and path.
    """
    groups = []
    paths = sorted(paths)
    for _, group in groupby(enumerate(paths), sort_by_folder(paths)):
        groups.append(list(group))
    return groups


class FQDNParamType(click.ParamType):
    """Represent a click FQDN url parameter type."""

    name = 'FQDN'

    def convert(self, value, param, ctx):
        """Validate parameter value."""
        try:
            # pylint: disable=no-value-for-parameter
            schema = vol.Schema(vol.FqdnUrl())
            return schema(value)
        except vol.Invalid:
            self.fail('{} is not a valid FQDN url'.format(value), param, ctx)


'''@click.command(options_metavar='<options>')
@click.option('-r', '--remote', required=True, type=FQDNParamType())
@click.argument('files', required=True, type=click.Path(exists=True), nargs=-1)
@click.option(
    '-d', '--dest', required=True,
    type=click.Path(exists=True, file_okay=False, writable=True))
@click.option('-e', '--exclude',default='')
@click.option('-i', '--include',default='')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True)'''
def download(remote, dest, files, username, password, exclude='', include=''):
    """Download files matching pattern."""
    # pylint: disable=too-many-arguments, too-many-locals
    print('in download')
    root_req = request(remote, (username, password))
    for myfile in files:
        print(myfile)
        try:
          mypath=os.path.join(dest,myfile)
          print(mypath)
          #os.makedirs(mypath)
        except FileExistsError:
          print('fail')
          pass
        #myfile = load_csv(myfile)

        folder_name = os.path.basename(os.path.dirname(mypath))
        print(folder_name)
        [folder_url] = parse_page(
                root_req.text, remote, include='/{}/'.format(folder_name))
        folder_req = request(folder_url, (username, password))
        base_name = os.path.basename(mypath)
        found = parse_page(folder_req.text, folder_url, exclude, base_name + include)
        if not found:
            print(
                'No files found for', folder_url + base_name + include,
                'with exclude', exclude)
            continue
        for url in found:
            file_name = os.path.basename(url)
            save_path = os.path.join(dest,file_name)
            print('Download:', url)
            print('Destination:', save_path)
            # download and save file here using requests
            req = request(url, (username, password), stream=True)
            with open(save_path, 'wb') as file_handle:
                for chunk in req.iter_content(1024):
                    file_handle.write(chunk)

if __name__ == '__main__':
    pass
