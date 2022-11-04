import os
import sys
import importlib

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)
from app.common.string import to_snake_case


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('Arguments are too short')

    else:
        service_id = args[1]
        module_name = to_snake_case(service_id)
        module = importlib.import_module('services.%s.main' % module_name)
        dbc = module.DbConverter()
        dbc.main()
