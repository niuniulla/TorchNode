"""
 This creates the main Ui of the application.
 There are 4 main part of the app:
    
    * node_window: the window contains nodes for model construction
    * layer_window: window containing available layer definition
    * info_window: window displaying the selected node information
    * group_windows: 3 optional windows for group management

"""

import dearpygui.dearpygui as dpg
from .manager_info import ModelManager
from .theme import ColorPalette
from .template import ModelConstructor

from .callback_functions import add_node_callback, \
                                node_link_callback, \
                                node_delink_callback, \
                                drag_select_nodes_callback, \
                                group_selected_nodes_callabck, \
                                delete_node_callback, \
                                group_editor_callback, \
                                group_change_callback, \
                                group_selected_callback, \
                                display_layer_info_callback, \
                                save_layout_callback, \
                                output_torch_class_callback, \
                                output_layers_callback, \
                                check_model_callback, \
                                load_layer_callback, \
                                output_model_callback, \
                                output_group_callback, \
                                save_callback, \
                                load_template_callback


##########################################################################################
#                                                                                        #
#                                       item names                                       #
#                                                                                        #
##########################################################################################


# node window
node_editor_name = "NodeEditor"
node_group_name = "nodes"
node_handler_name = "node_inputs"
input_node = "input_node"
node_editor_name = "NodeEditor"
node_group_name = "nodes"

# layer window
layer_window_name = "layer_add_window"

# info window
info_window_name = "layer_info"
group_combo_selector_name = "group_combo"
group_listbox = "group_listbox"

# group window
group_edit_window_name = "group_input_win"
group_group_window_name = "group_popup"
group_manager_window_name = "group_manager"
group_yes = "group_yes"
group_no = "group_no"

# model data
model_data = ModelManager( "layers_definition.json" )
model_json_file = "./model_def.json"
model_renderer = ModelConstructor("template.j2", model_data)


##########################################################################################
#                                                                                        #
#                                         Windows                                        #
#                                                                                        #
##########################################################################################


####################################### node window ######################################

def on_resize() :
    dpg.set_viewport_width(100)
    dpg.set_viewport_height(100)


def node_window( width=1200, height=800 ) :
        
        global model_data

        with dpg.window( label="Model Editor", width=width, height=height ) :

            with dpg.group( tag=node_group_name, 
                            drop_callback=add_node_callback, 
                            user_data=model_data,
                            width=5000,
                            height=5000) :
                    
                with dpg.node_editor( tag=node_editor_name, 
                                      callback=node_link_callback, 
                                      user_data=model_data,
                                      width=2000,
                                      height=2000
                                    ) :
                    
                    with dpg.node( tag=input_node, label="Input", user_data=model_data ) :

                        with dpg.node_attribute( label="Node A1", 
                                                 attribute_type=dpg.mvNode_Attr_Static, 
                                                 user_data=model_data
                                               ) :
                            
                            pass

                        with dpg.node_attribute( label="Node A2", 
                                                 attribute_type=dpg.mvNode_Attr_Output
                                               ) :
                            
                            dpg.add_input_int(label="F1", width=100)
                            dpg.add_input_int(label="F2", width=100)

        with dpg.handler_registry( label=node_handler_name ) :

            dpg.add_key_release_handler( key=dpg.mvKey_Delete, 
                                         callback=delete_node_callback, 
                                         user_data=model_data
                                       )
            
            dpg.add_mouse_click_handler( callback=display_layer_info_callback, 
                                         user_data=model_data
                                       )
            
            dpg.add_mouse_drag_handler( callback=drag_select_nodes_callback, 
                                        user_data=model_data
                                      )
            
            dpg.add_mouse_release_handler( callback=group_selected_nodes_callabck, 
                                           user_data=model_data
                                         )  


################################### layer window #########################################


# window for adding layers
def layer_manager_window() :

    global model_data
        
    with dpg.window( tag=layer_window_name, label="Modules", no_close=True ) :

        def add_button( layer ) :

            dpg.add_button( tag=layer["type"], label=layer["type"], width=-1 )

            with dpg.drag_payload( parent=layer["type"], 
                                   user_data=model_data, 
                                   drag_data=[model_data, layer]
                                 ) :
                
                dpg.add_text( layer["type"] )
        
        dpg.add_text( "Drag the button to Module Editor to construct the model.", wrap=200 )
        dpg.add_spacer()
                
        with dpg.group( tag="buttons" ):
        
            for category, layers in model_data.layer_data.items():

                dpg.add_text( f"{category}", color=ColorPalette.DIM_GRAY )

                for k in layers:

                    add_button( k )

                dpg.add_separator()

    dpg.focus_item( layer_window_name )


################################### info_window ##########################################


# window to show layer properties
def layer_property_window() :

    with dpg.window( tag=info_window_name, label="Layer Info", pos=(800, 0) , no_close=True ) :

        dpg.add_text( "Property information on selected layer (node). Highlighted " + 
                      "properties can be modified directly on the window.", 
                      wrap=200 
                    )
        
        dpg.add_spacer()
        
        dpg.add_separator()

    dpg.focus_item( info_window_name )


################################### group windows ########################################


# window to manage group
def group_manager_window() :

    global model_data
        
    with dpg.window( tag=group_manager_window_name, label="Group", pos=(800, 0) , no_close=True ) :

        dpg.add_text( "Group Manager" )
        dpg.add_separator()

        dpg.add_listbox(tag="group_listbox", 
                        items=model_data.get_group_names(), 
                        width=-1, num_items=10
                    )
        
        with dpg.group( horizontal=True ) :

            dpg.add_button( tag="group_edit",
                            label="Edit", 
                            callback=group_editor_callback, 
                            user_data=model_data
                          )
            
            dpg.add_button( tag="group_remove", 
                            label="Remove",
                            callback=group_editor_callback,
                            user_data=model_data
                        )
            

# window to edit group element, called by group manager
def group_editor_window() :

    global model_data

    group_name = dpg.get_value( "group_listbox" ) # the window is related to "group_listbox"
    
    with dpg.window( tag=group_edit_window_name, 
                     label="input", 
                     autosize=True, 
                     show=False,
                     no_focus_on_appearing=True,
                     no_close=True 
                   ) :

        with dpg.group() :

            dpg.add_text( "Enter a valid group name:" )

            dpg.add_input_text( tag="input_group_name", default_value=group_name )

            dpg.add_text( "Select a group type:" )

            dpg.add_combo( tag="input_group_type", 
                           default_value=model_data.get_group_attribute( group_name, "type" ), 
                           items=["default", "Sequential", "ModuleList"]
                         )
            
            dpg.add_text( "Pick a color:" )

            color = model_data.get_group_attribute( group_name, "color" )

            dpg.add_color_picker( tag="group_color_picker", 
                                  default_value=color, 
                                  label="Color Me", 
                                  no_inputs=True
                                )
            
            with dpg.group( horizontal=True ) :

                dpg.add_button( tag = group_edit_window_name + "_add",
                                label="Add", 
                                callback=group_change_callback, 
                                user_data=model_data,
                              )
                dpg.add_button( tag = group_edit_window_name + "_update",
                                label="Update", 
                                callback=group_change_callback, 
                                user_data=model_data
                              )
                dpg.add_button( label="Cancel", 
                                callback=lambda: dpg.configure_item(group_edit_window_name, show=False)
                              )


# window popup to group nodes
def group_group_window() :

    global model_data

    with dpg.window( tag=group_group_window_name, label="group", pos=(300, 300), show=False, no_close=True ) :
            
            dpg.add_text( "Group together? If yes, select a group." )

            dpg.add_combo(  tag=group_combo_selector_name, 
                            items=["Select Group..."] + model_data.get_group_names(), 
                            default_value="Select Group...",
                         )
            
            with dpg.group( horizontal=True ) :

                dpg.add_button( tag = group_yes,
                                label="Yes", 
                                callback=group_selected_callback, 
                                user_data=model_data 
                            )
                
                dpg.add_button( tag=group_no,
                                label="No", 
                                callback=group_selected_callback,
                                user_data=model_data 
                              )


######################################## menubar #########################################       


# menubar
def menubar():

    global model_data
        
    with dpg.viewport_menu_bar() :

        with dpg.menu( label="File" ) :

            dpg.add_menu_item( label="New Project" )

            dpg.add_separator()

            dpg.add_menu_item( label="Output Layers", 
                               callback=output_layers_callback, 
                               user_data=model_data
                             )

            dpg.add_menu_item( label="Output Model", 
                               callback=output_model_callback, 
                               user_data=model_data
                             )
            
            dpg.add_menu_item( label="Output Group", 
                               callback=output_group_callback, 
                               user_data=model_data
                             )

            dpg.add_menu_item( label="Save", callback=save_callback, user_data=model_data )

            dpg.add_menu_item( label="Save Layout", callback=save_layout_callback )
            
            dpg.add_separator()

            dpg.add_menu_item( label="Load", 
                               callback=load_layer_callback, 
                               user_data=model_data 
                             )
            
            dpg.add_menu_item( label="Load Group", enabled=False )

            dpg.add_menu_item( label="Load Template", 
                               callback=load_template_callback, 
                               user_data=model_renderer 
                             )

            dpg.add_separator()

            dpg.add_menu_item( label="Exit", callback=lambda: dpg.stop_dearpygui() )


        with dpg.menu( label="Run" ) :

            dpg.add_menu_item( label="Generate", 
                               callback=output_torch_class_callback, 
                               user_data=[model_renderer, model_data]
                             )
            dpg.add_menu_item( label="Validate", callback=check_model_callback )


        with dpg.menu( label="View" ) :

            dpg.add_menu_item( label="All_Panels", callback=output_layers_callback )

            with dpg.menu( label="View" ) :

                dpg.add_menu_item( label="Buttons", callback=lambda : dpg.show_item("Layers") )
                dpg.add_menu_item( label="Infos", callback=lambda : dpg.show_item("layer_info") )



##########################################################################################
#                                                                                        #
#                                       Application                                      #
#                                                                                        #
##########################################################################################

    
def create_app(width, height) :

    # window to manage nodes
    node_window()

    # window for adding layers
    layer_manager_window()

    # layer property
    layer_property_window()

    # window to manage group
    group_manager_window()
    group_editor_window()
    group_group_window()
        
    # menubar
    menubar()
    