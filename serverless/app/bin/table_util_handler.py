import os
import sys
import argparse
from pprint import pprint

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

from app.models.dynamodb import (
    SiteConfig,
    Service,
    ServiceConfig,
    AdminUserConfig,
    Post,
    PostGroup,
    Comment,
    CommentCount,
    Category,
    Tag,
    PostTag,
    File,
    VoteCount,
    VoteLog,
    ShortenUrl,
    ShortenUrlDomain,
)

allowed_tables = [
    'site_config',
    'service',
    'service_config',
    'admin_user_config',
    'post',
    'post_group',
    'comment',
    'comment_count',
    'category',
    'tag',
    'post_tag',
    'file',
    'vote_count',
    'vote_log',
    '.contact',
    'shorten_url',
    'shorten_url_domain',
]

class TableUtilHandler:
    def __init__(self):
        self.allowed_tables = allowed_tables

    def __del__(self):
        pass

    def main(self, table, operation):

        if table not in self.allowed_tables:
            print(f"Error: Invalid table name '{table}'.")
            return

        # Generate class name from table name as PasscalCase
        class_name = ''.join(word.capitalize() for word in table.split('_'))
        # Get class object from class name using globals()
        model_class = globals()[class_name]

        if operation == 'scan':
            items = model_class.scan()
            pprint(items)

        elif operation == 'truncate':
            model_class.truncate()
            print(f'{class_name}.delete() executed.')

        elif operation == 'delete':
            model_class.delete_table()
            print(f'{class_name}.delete_table() executed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('table', choices=allowed_tables, help="Choose the table: 'field' or 'post'")
    parser.add_argument('operation', choices=['scan', 'delete', 'truncate'], help="Choose the operation: 'scan' or 'delete'")
    args = parser.parse_args()

    scanner = TableUtilHandler()
    scanner.main(args.table, args.operation)
