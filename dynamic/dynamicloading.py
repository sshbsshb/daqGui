import configparser
from importlib import import_module


# Read the .ini file
config = configparser.ConfigParser()
config.read('test.ini')

# Get the module, class, and method names from the .ini file
module_name = config.get('class_info', 'module_name')
class_name = config.get('class_info', 'class_name')
method_name = config.get('class_info', 'method_name')

# Dynamically import the class and method
module = import_module(module_name)
ClassObj = getattr(module, class_name)

# Create an object of the class
obj = ClassObj()

# Call the specified method on the object
method = getattr(obj, method_name)
method()