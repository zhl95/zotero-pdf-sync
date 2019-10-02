
from pyzotero import zotero
import pprint as pt
import os
import copy
import shutil
import time
import datetime
##########################################################################################
##usually get keyerror, filename item's parent is not on item dict. The reason is this item is in unfiled items in
# windows zotero software (a duplicated one, beside the copy in some categories). delete the unfiled item it works.
##########################################################################################

library_id = 'xxx'
library_type = 'user'
api_key = 'xxx'

win_basepath = r'C:\Users\xxx\Zotero\storage'
# pad_basepath = r'./test_mk_dirs'
pad_basepath = r'C:\Users\xxx\Dropbox\xxx\zotero-pdfs'


def get_pdf_file_date(pdf_file):
    time_s = os.path.getmtime(pdf_file)
    return datetime.datetime.fromtimestamp(time_s)



def get_item_map(items):
    map_dict = {}
    for dict_ in items:
        tmp_dict = {}
        print(dict_['key'])
        try:
            collections_ = dict_['data']['collections']
            print("collections_: ", collections_)
        except KeyError:
            collections_ = None
        finally:
            tmp_dict['collections'] = collections_

        try:
            filename_ = dict_['data']['filename']
        except KeyError:
            filename_ = None
        finally:
            tmp_dict['filename'] = filename_

        try:
            up_ = dict_['data']['parentItem']
        except KeyError:
            up_ = None
        finally:
            tmp_dict['parentItem'] = up_
            map_dict[dict_['key']] = tmp_dict

    pt.pprint(map_dict)
    return map_dict


def get_collection_tree(collections):
    map_dict = {}
    for dict_ in collections:
        tmp_dict = {}
        print(dict_['data']['name'])

        tmp_dict['parent'] = dict_['data']['parentCollection']
        tmp_dict['name'] = dict_['data']['name']
        map_dict[dict_['key']] = tmp_dict
    pt.pprint(map_dict)
    return map_dict

# def tree_path():


def mk_path(collections_map, base_dir):
    for key_, val_ in collections_map.items():
        if val_['parent'] == False:
            folder = os.path.join(base_dir, val_['name'])
        else:
            print("val_['parent']: ", type(val_['parent']))
            folder = os.path.join(base_dir, collections_map[val_['parent']]['name'], val_['name'])
        if not os.path.exists(folder):
            os.makedirs(folder)


def get_path(collections_map, base_dir):
    for key_, val_ in collections_map.items():
        if val_['parent'] == False:
            folder = os.path.join(base_dir, val_['name'])
            if not os.path.exists(folder):
                os.makedirs(folder)
        else:
            print("val_['parent']: ", type(val_['parent']))
            val_['name'] = collections_map[val_['parent']]['name' ] +'/ ' +val_['name']
            val_['parent'] = False
            # del collections_map[val_['parent']]
            print("val_['name']: ", val_['name'])
            get_path(collections_map, base_dir)



def win2pad(item_map, collections_map_flatten, win_basepath, pad_basepath):
    for key_, val_ in item_map.items():
        if val_['filename'] is not None:
            win_file = os.path.join(win_basepath, key_, val_['filename'])
            assert os.path.isfile(win_file), "attachment is not on this PC!!"
            # print(os.path.isfile(win_file), win_file)
            if val_['parentItem'] is not None:
                collection_keys = item_map[val_['parentItem']]['collections']
            else:
                assert val_['collections'] is not None, "val_['collections'] shoudn't be None"
                collection_keys = val_['collections']
            for idx, collection_key_ in enumerate(collection_keys):
                path_str = collections_map_flatten[collection_key_]['name']
                pad_file = os.path.join(pad_basepath, path_str, val_['filename'])
                if idx == 0:
                    print(pad_file)
                    if not os.path.isfile(pad_file):
                        shutil.copy2(win_file, pad_file)
                    else:
                        pad_file_time = get_pdf_file_date(pad_file)
                        win_file_time = get_pdf_file_date(win_file)
                        if win_file_time >pad_file_time:
                            shutil.copy2(win_file, pad_file)

                else:
                    # path_str = collections_map_flatten[collection_key_]['name']
                    pad_file += "_ " +collections_map_flatten[collection_keys[0]]['name' ] +'.txt'
                    open(pad_file, 'a').close()
                    print(pad_file)

def sync(mode, item_map, collections_map_flatten, win_basepath, pad_basepath):
    for key_, val_ in item_map.items():
        if val_['filename'] is not None:
            win_file = os.path.join(win_basepath, key_, val_['filename'])
            if not win_file.endswith(".pdf"):
                continue

            if mode == 'win2pad':
                assert os.path.isfile(win_file), "attachment {} is not on this PC!!".format(win_file)

            # print(os.path.isfile(win_file), win_file)
            if val_['parentItem'] is not None:
                collection_keys = item_map[val_['parentItem']]['collections']
            else:
                assert val_['collections'] is not None, "val_['collections'] shoudn't be None"
                collection_keys = val_['collections']
            for idx, collection_key_ in enumerate(collection_keys):
                path_str = collections_map_flatten[collection_key_]['name']
                pad_file = os.path.join(pad_basepath, path_str, val_['filename'])

                if not pad_file.endswith(".pdf"):
                    continue
                no_ext_file = val_['filename'].replace(".pdf", "")
                # str.endswith(suffix)
                pad_file_exp = os.path.join(pad_basepath, path_str, no_ext_file, no_ext_file +"-Exported.pdf")

                if idx == 0:
                    print(pad_file)
                    if mode == 'win2pad':
                        assert os.path.isfile(win_file), "attachment is not on this PC!!"
                        if not os.path.isfile(pad_file):
                            shutil.copy2(win_file, pad_file)
                        else:
                            pad_file_time = get_pdf_file_date(pad_file)
                            win_file_time = get_pdf_file_date(win_file)
                            if win_file_time >pad_file_time:
                                shutil.copy2(win_file, pad_file)
                    else:
                        assert os.path.isfile(pad_file), "attachment is not on remote folder (Dropbox)!!"
                        if not os.path.isfile(win_file):
                            shutil.copy2(pad_file, win_file)
                        elif os.path.isfile(pad_file_exp):
                            pad_file_time = get_pdf_file_date(pad_file)
                            pad_file_exp_time = get_pdf_file_date(pad_file_exp)
                            win_file_time = get_pdf_file_date(win_file)
                            if pad_file_time <pad_file_exp_time:
                                shutil.copy2(pad_file_exp, pad_file)
                            if win_file_time <pad_file_exp_time:
                                shutil.copy2(pad_file, win_file)
                        else:
                            pad_file_time = get_pdf_file_date(pad_file)
                            win_file_time = get_pdf_file_date(win_file)
                            if win_file_time <pad_file_time:
                                shutil.copy2(pad_file, win_file)

                else:
                    # path_str = collections_map_flatten[collection_key_]['name']
                    print(1, pad_file)
                    other_collect = collections_map_flatten[collection_keys[0]]['name' ]
                    in1 = ('/' in other_collect)
                    in2 = ('\\' in other_collect)
                    print(in1, in2)
                    other_collect = other_collect.replace('/', '.')
                    other_collect = other_collect.replace('\\', '.')

                    print("other_collect: ", other_collect)
                    pad_file += "_ " +other_collect +'.txt'
                    print(2, pad_file)
                    open(pad_file, 'a').close()
                    





zot = zotero.Zotero(library_id, library_type, api_key)
# items = zot.top(limit=5)
# items = zot.items()
items = zot.everything(zot.items())  #items() only gives you 100 items, use everything like this. top() only gives you 25 top item (parent contains attchments), use everything also.

collections = zot.collections()
# print(items)
# print(len(items))
# print(len(collections))
# pt.pprint((collections))
# pt.pprint((items))

item_map = get_item_map(items)
collection_tree = get_collection_tree(collections)

collection_tree_flatten = copy.deepcopy(collection_tree)
# mk_path(collection_tree, r'C:\Users\zhengl11\Dropbox (Personal)\research\docs\zotero-pdfs')
# get_path(collection_tree_flatten, './test_mk_dirs')





get_path(collection_tree_flatten, pad_basepath)

collect_file = open("./test_mk_dirs/collections.txt", "w", encoding="utf8")
collect_flatten_file = open("./test_mk_dirs/collects_flatten.txt", "w", encoding="utf8")
item_file = open("./test_mk_dirs/items.txt", "w", encoding="utf8")
item_map_file = open("./test_mk_dirs/items_map.txt", "w", encoding="utf8")

# with open("./test_mk_dirs/collections.txt", 'w', encoding="utf8") as out:
#     pt.pprint(collection_tree, stream=out)

pt.pprint(collection_tree, collect_file)
pt.pprint(collection_tree_flatten, collect_flatten_file)
pt.pprint(items, item_file)
pt.pprint(item_map, item_map_file)

pt.pprint(items)
sync('win2pad', item_map, collection_tree_flatten, win_basepath, pad_basepath)
sync('pad2win', item_map, collection_tree_flatten, win_basepath, pad_basepath)









