import glob
import os.path
import sys
from itertools import chain

from jinja2 import Environment, ChoiceLoader, FileSystemLoader, select_autoescape
from weasyprint import HTML


class PdfRenderer:
    template_path = None
    template_filename = None

    def __init__(self, templates_path=None):
        paths = templates_path or []
        local_paths = (glob.glob('{}/*/templates/'.format(path)) for path in sys.path[:2])

        if isinstance(paths, str):
            paths = [paths]

        if self.template_path:
            paths.append(self.template_path)

        all_paths = (path for path in chain(local_paths, paths) if path)
        self._environment = Environment(
            loader=ChoiceLoader(FileSystemLoader(path) for path in all_paths),
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
