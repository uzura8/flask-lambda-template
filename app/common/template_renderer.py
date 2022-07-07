from os import  path
from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    env = None
    tmpl_dir_path = None

    def __init__(self, tmpl_dir_path=None, encoding='utf8'):
        if tmpl_dir_path is None:
            tmpl_dir_path = path.dirname(__file__) + '/../../config/templates'

        self.tmpl_dir_path = tmpl_dir_path
        self.env = Environment(
            loader=FileSystemLoader(tmpl_dir_path, encoding=encoding),
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]'
        )


    def render(self, tmpl_rel_path, params):
        tmpl = self.env.get_template(tmpl_rel_path)
        return tmpl.render(inputs=params)


    def check_exists_tmplate(self, tmpl_rel_path):
        tmpl_path = '%s/%s' % (self.tmpl_dir_path, tmpl_rel_path)
        return path.exists(tmpl_path)
