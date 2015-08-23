__author__ = 'Nick Eng, nickeng@gmail.com'
import requests
import json
import sys
import xml.etree.ElementTree as ET

with open('settings.json') as f:
    settings = json.loads(f.read())
access_token = settings['access_token']
client_id = settings['client_id']

api_headers = {'X-Client-ID': client_id,
               'X-Access-Token': access_token,
               'Content-Type': 'application/json'}

# Separator that delimits chained script filter commands
separator = '>>'

# XML constructor for output to script filter
def to_xml(titles, args=None, valids=None, autocompletes=None):

    root = ET.Element('items')

    if len(titles) < 1:
        titles = ['Nothing here']

    for i, thing in enumerate(titles):
        item = ET.SubElement(root, 'item')
        if args is not None:
            item.set('arg', args[i])
        if valids is None:
            item.set('valid', 'NO')
        else:
            item.set('valid', valids[i])
        if autocompletes is not None:
            item.set('autocomplete', autocompletes[i])

        title = ET.SubElement(item, 'title')
        title.text = titles[i]

    return ET.tostring(root)

# TODO: Make showing things preserve order in list

# TODO: Make subtext number of items -- slow with current API structure
def get_lists():
    r = requests.get('https://a.wunderlist.com/api/v1/lists',
                     headers = api_headers)
    list_names = [i['title'] for i in r.json()]
    # autocomplete_paths = [i + ' {0} '.format(separator) for i in list_names]
    return to_xml(list_names, autocompletes=list_names)

# TODO: make subtext task description and other things
def show_list(list_name):
    # Get list_id for the list that you want to show
    r = requests.get('https://a.wunderlist.com/api/v1/lists',
                     headers = api_headers)
    list_id_dict = {i['title'].lower(): i['id'] for i in r.json()}
    list_id = list_id_dict[list_name.lower()]

    # Actually retrieve the list
    r = requests.get('https://a.wunderlist.com/api/v1/tasks',
                     headers=api_headers,
                     params={'list_id': str(list_id)})
    task_titles = [i['title'] for i in r.json()]
    task_ids = [i['id'] for i in r.json()]
    task_revisions = [i['revision'] for i in r.json()]
    task_args = ['{0};%;{1};%;{2}'.format(i, j, k) \
                 for i, j, k in zip(task_ids, task_revisions, task_titles)]
    # Create array of 'YES' to pass to to_xml to make things selectable
    valids = ['NO']*len(task_titles) #Not valid since complete_task doesn't work
    return to_xml(task_titles, args=task_args, valids=valids)

def add_task(task_title):
    # Get first list_id which should be the inbox.
    # This is where the new task will be placed by default.
    r = requests.get('https://a.wunderlist.com/api/v1/lists',
                     headers=api_headers)
    first_list_id = r.json()[0]['id']

    # Actually add the task
    r = requests.post('https://a.wunderlist.com/api/v1/tasks',
                      headers=api_headers,
                      data=json.dumps({'list_id': first_list_id,
                                       'title': task_title}))
    if 200 <= r.status_code < 300:
        return task_title
    else:
        return 'Adding action failed'

def complete_task(task_id, revision, task_name=None):
    # This shit doesn't work what the fuck.
    r = requests.patch('https://a.wunderlist.com/api/v1/tasks/{0}'.format(task_id),
                      headers=api_headers,
                      data={'revision': revision})
    if 200 <= r.status_code < 300:
        if task_name is not None:
            return task_name
        else:
            return 'Task deleted'
    else:
        return 'Deletion action failed'

def parse_complete_string(parse_string, delimiter):
    task_id = parse_string.split(delimiter)[0]
    revision = parse_string.split(delimiter)[1]
    try:
        task_name = parse_string.split(delimiter)[2]
    except IndexError:
        task_name = None
    remove_task(task_id, revision, task_name)
    return

def define_settings(client_id, access_token):
    with open('settings.json') as f:
        settings = json.loads(f.read())

    settings['client_id'] = client_id
    settings['access_token'] = access_token

    with open('settings.json', 'w+') as f:
          f.write(json.dumps(settings))
    return

def setup(query):
    arguments = query.split(separator)
    client_id = arguments[0]
    access_token = arguments[1]
    define_settings(client_id, access_token)
    return (client_id, access_token)

if __name__ == '__main__':
    assert len(sys.argv) > 1, "command argument is required"
    command = sys.argv[1]

    try:
        query = sys.argv[2]
    except IndexError:
        query = ''

    if command == 'add':
        print add_task(query)

    elif command == 'show':
        if query =='':
            print get_lists()
        else:
            print show_list(query)

    # TODO: selecting a task shown marks as complete. Bug in Wunderlist API
    elif command == 'remove':
        parse_complete_string(query, ';%;')

    elif command == 'setup':
        client_id, access_token = setup(query)
        print 'Client ID: {0}, Access Token: {1}'\
            .format(client_id, access_token)