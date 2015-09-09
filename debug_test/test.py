# -*- coding: utf-8 -*-

import sys
import xml.etree.ElementTree as ET

# test_dict = {'a´´´´ÅÅÅ´´ÅÎÎÎÏÍÒˆ„ÏıÔÍÓÔÍÏıÅÍ¯ÅÍåå∂ß˚˜≤√åß'.decode('utf-8').lower(): 234, 'b': 2}
test_dict = {'Å'.decode('utf-8'): 234, 'b': 2}

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

    return ET.tostring(root, encoding='utf-8')

if __name__ == '__main__':
    query = sys.argv[1].decode('utf-8')
    output_value = test_dict[query]
    print to_xml(str(output_value))
    # print str(output_value)