import glob
import os.path
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML


class PdfRenderer:
    template_filename = None

    def __init__(self, templates_path=None):
        default_templates_path = glob.glob('{}/*/templates/'.format(sys.path[0]))

        if isinstance(templates_path, str):
            templates_path = [templates_path]

        templates_path = templates_path or []
        templates_path += default_templates_path

        self._environment = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=select_autoescape(['html', 'xml']),
        )
        self.template = self._environment.get_template(self.template_filename)

    def render_html(self, context: dict):
        return self.template.render(**context)

    def render_pdf(self, context: dict):
        raw_html = self.render_html(context)
        base_url = os.path.dirname(self.template.filename)
        html = HTML(string=raw_html, base_url=base_url)
        return html.render()

    def render(self, *args, **kwargs):
        raise NotImplementedError()
