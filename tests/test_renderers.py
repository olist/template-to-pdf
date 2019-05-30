import os
import tempfile
from unittest import mock

from jinja2.exceptions import TemplateNotFound

import pytest

import template_to_pdf
from template_to_pdf import PdfRenderer

CURRENT_PATH = os.path.dirname(__file__)


class MyPdfRenderer(PdfRenderer):
    template_filename = 'foo.html'


@pytest.fixture
def pdf_renderer():
    return MyPdfRenderer(templates_path=[CURRENT_PATH])


@pytest.fixture
def temp_templates_folder():
    app_path = os.path.dirname(template_to_pdf.__file__)
    template_path = f'{app_path}/templates'
    os.mkdir(template_path)
    filename = f'{template_path}/foo.html'
    with open(filename, 'w') as f:
        f.write('foo')

    yield template_path

    os.remove(filename)
    os.rmdir(template_path)


def test_pdf_renderer_custom_template_path():
    with tempfile.TemporaryDirectory() as tmp_dirname:
        filename = f'{tmp_dirname}/foo.html'
        with open(filename, 'w') as f:
            f.write('foo')

        pdf_renderer = MyPdfRenderer(templates_path=tmp_dirname)

    assert pdf_renderer.template.filename == filename
    assert pdf_renderer._environment
    assert pdf_renderer.template


def test_pdf_renderer_template_path_class_attribute():
    with tempfile.TemporaryDirectory() as tmp_dirname:
        class CustomPdfRenderer(PdfRenderer):
            template_path = tmp_dirname
            template_filename = 'foo.html'

        filename = f'{tmp_dirname}/foo.html'
        with open(filename, 'w') as f:
            f.write('foo')

        pdf_renderer = CustomPdfRenderer()

    assert pdf_renderer.template.filename == filename
    assert pdf_renderer._environment
    assert pdf_renderer.template


def test_pdf_renderer_default_template_path(temp_templates_folder):
    pdf_renderer = MyPdfRenderer()

    assert pdf_renderer._environment
    assert pdf_renderer.template
    assert pdf_renderer.template.filename == f'{temp_templates_folder}/foo.html'


def test_pdf_renderer_default_template_path_dirty_sys_path(monkeypatch, temp_templates_folder):
    import sys
    monkeypatch.setattr(sys, 'path', ['dirt'] + sys.path)

    pdf_renderer = MyPdfRenderer()

    assert pdf_renderer._environment
    assert pdf_renderer.template
    assert pdf_renderer.template.filename == f'{temp_templates_folder}/foo.html'


def test_pdf_renderer_invalid_file():
    with pytest.raises(TemplateNotFound):
        MyPdfRenderer()


def test_pdf_renderer_render(pdf_renderer):
    with pytest.raises(NotImplementedError):
        pdf_renderer.render()


def test_pdf_renderer_render_html(pdf_renderer):
    context = {'foo': 'bá'}

    rendered = pdf_renderer.render_html(context)

    assert context['foo'] in rendered


@mock.patch('template_to_pdf.HTML')
def test_pdf_renderer_render_pdf(mock_html, pdf_renderer):
    pdf_renderer.render_html = mock.Mock()
    context = {'foo': 'bá'}

    assert pdf_renderer.render_pdf(context)

    pdf_renderer.render_html.assert_called_once_with(context)
    mock_html.assert_called_once_with(
        string=pdf_renderer.render_html.return_value,
        base_url=os.path.dirname(pdf_renderer.template.filename),
    )
    mock_html.return_value.render.assert_called_once_with()
