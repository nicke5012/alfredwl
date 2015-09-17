import requests
import json
import sys
import subprocess
import xml.etree.ElementTree as ET
from unicodedata import normalize
from workflow import Workflow

__author__ = 'Nick Eng, nickeng@gmail.com'

# Separator that delimits chained script filter commands
separator = '>>'

wf = Workflow()

# XML constructor for output to script filter
def to_xml(titles, args=(), valids=(), autocompletes=()):

    root = ET.Element('items')

    if len(titles) < 1:
        titles = ['Nothing here']

    for i, thing in enumerate(titles):
        item = ET.SubElement(root, 'item')
        if args:
            item.set('arg', args[i])
        if valids:
            item.set('valid', valids[i])
        else:
            item.set('valid', 'NO')
        if autocompletes:
            item.set('autocomplete', autocompletes[i])

        title = ET.SubElement(item, 'title')
        title.text = titles[i]

    return ET.tostring(root, encoding='utf-8')


def get_credentials():
    credentials = wf.get_password(u'alfredwl')
    client_id, access_token = credentials.split('::')
    return client_id, access_token


def get_lists(api_headers):
    r = requests.get('https://a.wunderlist.com/api/v1/lists',
                     headers=api_headers)
    list_names = [i['title'] for i in r.json()]
    return to_xml(list_names, autocompletes=list_names)


def get_valid_lists(api_headers):
    r = requests.get('https://a.wunderlist.com/api/v1/lists',
                     headers=api_headers)
    list_id_dict = {i['title'].lower(): i['id'] for i in r.json()}
    return list_id_dict


def show_list(api_headers, list_name):
    # TODO: speed this up
    # Get list_id for the list that you want to show
    valid_lists = get_valid_lists(api_headers)
    try:
        list_id = valid_lists[list_name.lower()]
    except KeyError:
        return to_xml(['No such list!'])

    # Actually retrieve the list
    r = requests.get('https://a.wunderlist.com/api/v1/tasks',
                     headers=api_headers,
                     params={'list_id': str(list_id)})
    task_titles = [i['title'] for i in r.json()]
    task_ids = [i['id'] for i in r.json()]
    task_revisions = [i['revision'] for i in r.json()]
    task_args = [u'{0};%;{1};%;{2}'.format(i, j, k)
                 for i, j, k in zip(task_ids, task_revisions, task_titles)]
    valids = ['YES']*len(task_titles)
    return to_xml(task_titles, args=task_args, valids=valids)


def add_task(api_headers, task_description):
    # Get list of valid lists
    valid_lists = get_valid_lists(api_headers)

    # Figure out which list to add to (Inbox or other)
    try:
        task_description_split = task_description.split('>>')
        target_list_name = task_description_split[0]
        task_title = task_description_split[1]
        target_list_id = valid_lists[target_list_name.lower()]
    except (IndexError, KeyError):
        target_list_name = 'inbox'
        task_title = task_description
        target_list_id = valid_lists[target_list_name.lower()]

    # Actually add the task
    r = requests.post('https://a.wunderlist.com/api/v1/tasks',
                      headers=api_headers,
                      data=json.dumps({'list_id': target_list_id,
                                       'title': task_title}))

    # Send back confirmation
    if 200 <= r.status_code < 300:
        return task_title + u' to ' + target_list_name
    else:
        return u'Add task failed'


def complete_task(api_headers, task_id, revision, task_name=None):
    # I have no idea why this doesn't work with Requests
    # r = requests.patch('https://a.wunderlist.com/api/v1/tasks/{0}'.format(task_id),
    #                   headers=api_headers,
    #                   data={'revision': revision})

    # Since this doesn't work with requests, I work with curl and subprocess instead
    client_id_header = 'X-Client-ID: {0}'.format(api_headers['X-Client-ID'])
    access_token_header = 'X-Access-Token: {0}'.format(api_headers['X-Access-Token'])
    url = 'https://a.wunderlist.com/api/v1/tasks/{0}'.format(task_id)
    data = '{{"revision": {0}, "completed": true}}'.format(revision)

    curl_call = subprocess.Popen(['curl', '-H', client_id_header, '-H',
                                  access_token_header, '-H',
                                  'Content-Type: application/json', url, '-X',
                                  'PATCH', '-d', data], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    output = json.loads(curl_call.communicate()[0])
    output = {'completed': True}

    if 'completed' in output and output['completed']==True:
        if task_name:
            return task_name
        else:
            return u'Task marked complete'
    else:
        return u'Completion action failed'


def parse_complete_string(api_headers, parse_string, delimiter):
    split_string = parse_string.split(delimiter)
    task_id = split_string[0]
    revision = split_string[1]
    try:
        task_name = split_string[2]
    except IndexError:
        task_name = None
    output = complete_task(api_headers, task_id, revision, task_name)
    return output


def setup(query):
    arguments = query.split(separator)
    client_id = arguments[0]
    access_token = arguments[1]
    wf.save_password(u'alfredwl', client_id + '::' + access_token)
    return client_id, access_token


if __name__ == '__main__':

    assert len(sys.argv) > 1, "command argument is required"
    command = sys.argv[1]

    try:
        query = normalize('NFC', sys.argv[2].decode('utf-8'))
    except IndexError:
        query = ''

    if command == 'setup':
        client_id, access_token = setup(query)
        print 'Client ID: {0}, Access Token: {1}'\
            .format(client_id, access_token)

    else:

        try:
            client_id, access_token = get_credentials()
        except:
            print to_xml(['Need to run setup!'])
            sys.exit(0)

        api_headers = {'X-Client-ID': client_id,
                       'X-Access-Token': access_token,
                       'Content-Type': 'application/json'}

        if command == 'add':
            print add_task(api_headers, query).encode('utf-8')

        elif command == 'show':
            if query == '':
                print get_lists(api_headers)
            else:
                print show_list(api_headers, query)

        elif command == 'complete':
            print parse_complete_string(api_headers, query, ';%;').encode('utf-8')

# Requests for Wunderlist API: Smartlists, ordering of lists/tasks