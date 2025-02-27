# -*- coding: utf-8 -*-
#import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

class JinjaRenderer:
    #    """
    #    Singleton Class: Initializes the Jinja environment and output directory.
    #    """
    _instance = None
    def __new__(cls, template_dir):
        if cls._instance is None:
            cls._instance = super(JinjaRenderer, cls).__new__(cls)
            cls._instance.template_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape()
            )
        return cls._instance


    #def __init__(self, template_dir):
    #    """
    #    Initializes the Jinja environment and output directory.
    #    """
    #    self.template_env = Environment(
    #        loader=FileSystemLoader(template_dir),
    #        autoescape=select_autoescape()
    #    )

    def render_templates(self, template, data, outputFile=''):
        """
        Renders Jinja templates
        """
        template = self.template_env.get_template(template)  # Assuming template name
        renderoutput = template.render(data=data)
        if outputFile=='':
            return renderoutput
        else:
            try:
                with open(outputFile, 'r') as f:
                    old_content = f.read()
            except FileNotFoundError:
                old_content = ""

            if old_content != renderoutput:
                with open(outputFile, 'w') as f:
                    f.write(renderoutput)
                    print(f"Content written to {outputFile}")
            else:
                print(f"Content is the same, skipping write to {outputFile}")
