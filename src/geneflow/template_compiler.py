"""This module contains the GeneFlow Template Compiler class."""


import jinja2

from geneflow.log import Log
from geneflow import GF_PACKAGE_PATH



class TemplateCompiler:
    """
    GeneFlow TemplateCompiler class.

    The TemplateCompiler class is used to generate files from Jinja2 templates
    packaged with the GeneFlow source.
    """

    @staticmethod
    def compile_template(
            template_path,
            template_name,
            compiled_name,
            **kwargs
    ):
        """
        Compile a GeneFlow template file.

        Args:
            template_path: search path for templates. If omitted, the
                GeneFlow package path of data/templates is used.
            template_name: name of the template file, must be stored in
                data/templates of the GeneFlow source package.
            compiled_name: full path of the compiled target file.
            kwargs: data to populate the template.

        Returns:
            On success: True.
            On failure: False.

        """
        # set default template path
        if not template_path:
            template_path = GF_PACKAGE_PATH / 'data/templates'

        # load template
        try:
            template_loader = jinja2.FileSystemLoader(
                searchpath=str(template_path)
            )
            template_env = jinja2.Environment(
                loader=template_loader,
                trim_blocks=True,
                lstrip_blocks=True
            )
            template = template_env.get_template(template_name)

        except jinja2.TemplateSyntaxError as err:
            Log.an().warning(
                'cannot load template, syntax error: %s [%s, %s]',
                template_name,
                str(err),
                str(err.lineno)
            )
            return False

        except jinja2.TemplateError as err:
            Log.an().warning(
                'cannot load template: %s [%s]',
                template_name,
                str(err)
            )
            return False

        # compile and write
        try:
            with open(str(compiled_name), 'w') as compiled_file:
                compiled_file.write(template.render(**kwargs))

        except IOError as err:
            Log.an().warning(
                'cannot write compiled template file: %s [%s]',
                compiled_name, str(err)
            )
            return False

        except jinja2.TemplateError as err:
            Log.a().warning(
                'cannot compile template: %s [%s]', template_name, str(err)
            )
            return False

        return True
