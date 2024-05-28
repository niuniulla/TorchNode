"""
 Template engin to generate script
"""

from jinja2 import Template, Environment, PackageLoader, FileSystemLoader
import os, json


class ModelConstructor :

    def __init__( self, template_file, model_manager ) :

        self.template_file = template_file

        self.env = Environment(loader=FileSystemLoader("./resources"))

        self.template = self.env.get_template(template_file)

        self.model_manager = model_manager
        

    def render_file( self ) :

        if self.model_file is None:
            return 
        
        f = open(self.model_file)
        data = json.load(f)

        res = self.template.render(model=data)


    def render( self ) :

        if self.model_manager is None:
            return
        
        grouped_data = self.model_manager.by_group()
        group_paths = {}

        for group_name, layers in grouped_data.items() :

            group_paths[group_name] = self.model_manager.bfs( group_name )

        res = self.template.render( model=grouped_data, paths=group_paths )

        print(res)


    def set_data( self, data ) :

        self.model_manager = data


    def set_file( self, file ) :
        
        self.model_file = file


    def set_template_file( self, template_file ) :

        self.template_file = template_file
        
        self.template = self.env.get_template(template_file)

