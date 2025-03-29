import importlib
import re
 
 
def check_list_contained(A, B):
  # convert list A to string
    A_str = ' '.join(map(str, A))
    # convert list B to string
    B_str = ' '.join(map(str, B))
    # find all instances of A within B
    instances = re.findall(A_str, B_str)
 
    # return True if any instances were found, False otherwise
    return len(instances) > 0
def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

def convertStrList(module_name, str_list):
    item_list = []
    for item in str_list:
        item_list.append(class_for_name(module_name, item)())
    return item_list

def convertBuffList(module_name, str_list):
    item_list = []
    for item in str_list:
        for level in class_for_name(module_name, item).levels:
            item_list.append(class_for_name(module_name, item)(level))
    return item_list
    