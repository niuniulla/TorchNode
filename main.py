import dearpygui.dearpygui as dpg
from src.application import create_app

# create context
dpg.create_context()
dpg.configure_app(docking=True, 
                  init_file="./resources/ui_init.ini")

# create app window
width=1400
height=800
create_app(width, height)

dpg.create_viewport(title='Torch Model Constructor', width=width, height=height)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

