"""
 This file contains all the callback function used in application (UI).
 They are grouped by the 4 main parts of the app (see application.py).

 For simplicity and uniformity, all functions have 3 parameters, but
 they may not be all used in all functions. 
"""

import dearpygui.dearpygui as dpg
from .theme import ColorPalette
from .template import ModelConstructor
import json, logging


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
group_edit = "group_edit"
group_remove = "group_remove"

# global variables
LinkList = []
selected_nodes = set()
old_selected_nodes = set()
old_selected_node = -1


##########################################################################################
#                                                                                        #
#                                        callbacks                                       #
#                                                                                        #
##########################################################################################


####################################### node window ######################################


def add_node_callback( sender, app_data, user_data ) :
        
    """
    called by "nodes"
    """
    
    model_data= app_data[0]
    layer = app_data[1]

    # get the mouse pos on the node editor
    node_pos = global_mouse_pos = dpg.get_mouse_pos( local=False )
    ref_screen_pos = dpg.get_item_rect_min( node_group_name )
    node_pos[0] = global_mouse_pos[0] - ref_screen_pos[0]

    # get node id
    node_id = dpg.generate_uuid()

    # create layer in model
    model_data.add_layer( node_id, layer )
    model_data.set_layer_pos( node_id, node_pos )

    add_node( node_id, model_data )
                            
    update_node_theme( node_id, model_data )

    # create display on window "layer_info"
    create_display_info( node_id, model_data )

    # update group list
    dpg.configure_item( "group_listbox", items=model_data.get_group_names() )



def node_input_callback( sender, app_data, user_data ) :

    """
    called by each created node
    """

    attribute = dpg.get_item_parent( sender )
    node_id = dpg.get_item_parent( attribute )
    label = dpg.get_item_label( sender )

    print( "input callback: ", app_data, "parent: ", node_id, "label: ", label )

    print( "changed value to: ", dpg.get_value(sender) )

    user_data.set_param_value( node_id, 
                               dpg.get_item_label(sender), 
                               dpg.get_value(sender)
                             )
    
    # update info item
    create_display_info( node_id, user_data, show=True )



def node_link_callback( sender, app_data, user_data ) :

    """
    called by "NodeEditor"
    """

    model_data = user_data

    if type(app_data) == tuple :

        link_id1, link_id2 = app_data
        
        dpg.add_node_link( link_id1, link_id2, parent=sender )

        links = ( dpg.get_item_alias(link_id1), dpg.get_item_alias(link_id2) )

        # update model_data
        
        node_ids = ( dpg.get_item_parent(link_id1), dpg.get_item_parent(link_id2) )

        model_data.assign_link( node_ids[0], node_ids[1], before=False )
        model_data.assign_link( node_ids[1], node_ids[0] )

        LinkList.append( links )

        create_display_info( node_ids[0], user_data, show=False )
        create_display_info( node_ids[1], user_data, show=False )



def node_delink_callback( sender, app_data, user_data ) :

    """
    called  by "NodeEditor"
    """

    link_id = app_data

    # update model_data on links
    # TODO
    parent = dpg.get_item_parent( link_id )
    print("linked_node: ", link_id)

    dpg.delete_item( link_id )


 
def drag_select_nodes_callback( sender, app_data, user_data ) :

    """
    called by input_handler : "node_inputs" - mouse_drag
    """

    global selected_nodes

    model_data = user_data

    selected_nodes.clear()

    selected_nodes = set( dpg.get_selected_nodes(node_editor_name) )

    # update node positions
    if len(selected_nodes) > 0 :

        for node in selected_nodes :

            model_data.set_layer_pos( node, dpg.get_item_pos(node) )


def group_selected_nodes_callabck( sender, app_data, user_data ) :

    """
    called by input_handler : "node_inputs" - mouse_release
    """

    global old_selected_nodes
    global selected_nodes

    model_data = user_data

    ids = model_data.get_all_layer_ids()

    nodes = set( i for i in selected_nodes if i in ids )

    if len(nodes) > 1 :

        show_group()

        # if the group window ouside of focus, bring it back
        if not dpg.is_item_hovered( group_group_window_name ) :
            dpg.focus_item( group_group_window_name )

        # get the selected group in combo
        dpg.configure_item( group_combo_selector_name, items=model_data.get_group_names() )


def delete_node_callback( sender, app_data, user_data ) :

    """
    called by input_handler : "node_inputs" - key_release 
    """

    model_data = user_data

    # delete links
    for link in dpg.get_selected_links( node_editor_name ) :
        print("linklink: ", link)
        
        # get the connected nodes' id
        node1 = dpg.get_item_parent( dpg.get_item_configuration(link)["attr_1"] )
        node2 = dpg.get_item_parent( dpg.get_item_configuration(link)["attr_2"] )

        # remove links from model
        model_data.remove_mutual_links( node1, node2 )

        # remove link
        dpg.delete_item( link )


    # delete nodes
    for selected_node in dpg.get_selected_nodes( node_editor_name ) :
        # Deleting node and attached links
        ## Extract all children of the deleted node
        selected_node_children = dpg.get_item_children(selected_node)[1]

        ## Extract all existing links in the Node Editor
        nodeEditor_links = dpg.get_item_children(node_editor_name)[0]

        ## Iterate through NodeEditor elements and delete attached links
        for link in nodeEditor_links:

            if dpg.get_item_configuration(link)["attr_1"] in selected_node_children or \
               dpg.get_item_configuration(link)["attr_2"] in selected_node_children :
                
                dpg.delete_item( link )

        ## Iterate trough LinkList and remove attached links
        for item in LinkList:

            for sub_item in item:

                if dpg.get_item_alias( selected_node ) in sub_item :

                    LinkList.remove( item ) 

        # Delete node
        dpg.delete_item( selected_node )

        # remove links
        node1, node2 = model_data.get_links( selected_node )

        if ( node1 != -1 ) :

            # remove link from model before
            model_data.remove_link( node1, before=False )

        if ( node2 != -1 ) :

            # remove link from model after
            model_data.remove_links( node2 )

        # delete info item
        info_lable = "Layer Attributes_" + str(selected_node)
        dpg.hide_item( info_lable )
        dpg.delete_item( info_lable )

        # remove layer from model
        model_data.remove_layer( selected_node )



def display_layer_info_callback( sender, app_data, user_data ) :

    global old_selected_node

    for selected_node in dpg.get_selected_nodes( node_editor_name ) :

        if not selected_node in user_data.get_all_layer_ids() :

            old_selected_node = -1
            return
        
        else :

            if old_selected_node == selected_node :

                return
            
            for layer_id in user_data.get_all_layer_ids() :

                item_name = "Layer Attributes_" + str(layer_id)  
                dpg.hide_item(item_name)

            print("selected_node", selected_node)

            old_selected_node = selected_node

            item_name = "Layer Attributes_" + user_data.get_layer_name(selected_node)

            create_display_info( selected_node, user_data, show=True )


# node helper functions
            

def update_node_theme( node_id, user_data ) :
    # create theme to change color

    model_data = user_data
    
    with dpg.theme() as item_theme:
        with dpg.theme_component( dpg.mvNode ) :

            group_name = model_data.get_group_name( node_id )
            color = model_data.get_group_attribute( group_name, "color" )
            link_theme_color = dpg.add_theme_color( dpg.mvNodeCol_TitleBar, 
                                                    color, 
                                                    category=dpg.mvThemeCat_Nodes
                                                  )
            
    dpg.bind_item_theme( node_id, item_theme )


def add_node( node_id, model_data ) :

    with dpg.node( tag=node_id, 
                   label=model_data.get_layer_name(node_id), 
                   parent=node_editor_name, 
                   pos=model_data.get_layer_pos(node_id) 
                 ) :

        dpg.add_node_attribute( label=" ", attribute_type=dpg.mvNode_Attr_Input )
        dpg.add_node_attribute( label=" ", attribute_type=dpg.mvNode_Attr_Output )
        
        with dpg.node_attribute( attribute_type=dpg.mvNode_Attr_Static ) :

            for p in model_data.get_params( node_id ) :
                print("p: ", p)

                if  bool(p) and not bool(p["default"]) :

                    match p["dtype"] :
                        
                        case "int" :
                            dpg.add_input_int( tag=str(node_id) + "_" + p["name"],
                                               label=p["name"], 
                                               default_value=int(p["default_value"]),
                                               callback=node_input_callback, 
                                               width=100, 
                                               user_data=model_data
                                             )
                        
                        case "float" :
                            dpg.add_input_float( tag=str(node_id) + "_" + p["name"],
                                                 label=p["name"],
                                                 default_value=float(p["default_value"]),
                                                 callback=node_input_callback, 
                                                 width=100, 
                                                 user_data=model_data
                                               )
                        
                        case "bool" :
                            dpg.add_combo( tag=str(node_id) + "_" + p["name"],
                                            label=p["name"], 
                                            default_value=bool(p["default_value"]),
                                            callback=node_input_callback, 
                                            width=100,
                                            items=[True, False],
                                            user_data=model_data
                                          )
                            
                        case _ :
                            dpg.add_input_text( tag=str(node_id) + "_" + p["name"],
                                                label=p["name"], 
                                                default_value=p["default_value"],
                                                callback=node_input_callback, 
                                                width=100,
                                                user_data=model_data
                                              )



################################### layer window #########################################

# None



################################### info_window ##########################################


def create_display_info( node_id, model_manager, show=False ) :

    """
    create info window items
    """

    print("create display for id: ", node_id)

    info_lable = get_info_item_name( node_id )

    if dpg.does_alias_exist( info_lable ) :

        dpg.delete_item( info_lable )

    with dpg.group( tag=info_lable, label=info_lable, parent=info_window_name, show=show ) :
        
        dpg.add_text( "ATTRIBUTES ", color=ColorPalette.DIM_GRAY )

        with dpg.group( horizontal=True ) :

            dpg.add_text( "Name  ", color=ColorPalette.PERU )

            dpg.add_input_text( default_value=model_manager.get_layer_name(node_id), 
                                callback=change_name_callback,
                                user_data=[model_manager, node_id],
                                on_enter=True,
                                width=-1
                              )
        
        with dpg.group( horizontal=True ) :

            dpg.add_text( "ID#   ", color=ColorPalette.DIM_GRAY )
            dpg.add_text( default_value=node_id )
        
        with dpg.group( horizontal=True ) :

            dpg.add_text( "Type  ", color=ColorPalette.GRAY )
            dpg.add_text( default_value=model_manager.get_layer_type(node_id) )
        
        with dpg.group( horizontal=True ) :

            dpg.add_text( "Before", color=ColorPalette.GRAY )
            dpg.add_text( default_value=model_manager.get_links(node_id)[0] )

        with dpg.group( horizontal=True ) :

            dpg.add_text( "After ", color=ColorPalette.GRAY )
            dpg.add_text( default_value=model_manager.get_links(node_id)[1] )

        dpg.add_separator()
        
        dpg.add_text( "PARAMETERS", color=ColorPalette.DIM_GRAY )

        for p in model_manager.get_params( node_id ) :

            if  not bool(p) :
                break

            print("params: ", p["name"])

            with dpg.group( horizontal=True ) :

                if int(p["enabled"]) :

                    dpg.add_text( p["name"], color=ColorPalette.PERU )

                else :
                    
                    dpg.add_text( str(p["name"]) + ": " + str(p["description"]), 
                                  color=ColorPalette.DIM_GRAY
                                )
                    continue

                match p["dtype"] :

                    case "int" :
                        dpg.add_input_int( default_value=p["value"], 
                                           callback=change_param_callback,
                                           user_data=[model_manager, node_id, p["name"], p["dtype"]],
                                           width=-1
                                         )
                    case "double" :
                        dpg.add_input_float( default_value=p["value"], 
                                             callback=change_param_callback,
                                             user_data=[model_manager, node_id, p["name"], p["dtype"]],
                                             width=-1
                                           )
                    case "float" :
                        dpg.add_input_float( default_value=p["value"], 
                                             callback=change_param_callback,
                                             user_data=[model_manager, node_id, p["name"], p["dtype"]],
                                             width=-1
                                           )
                    case "bool":
                        dpg.add_combo( default_value=p["value"], items=[True, False], 
                                       callback=change_param_callback,
                                       user_data=[model_manager, node_id, p["name"], p["dtype"]],
                                       width=-1
                                     )
                    case _:
                        dpg.add_input_text( default_value=p["value"], 
                                            callback=change_param_callback,
                                            user_data=[model_manager, node_id, p["name"], p["dtype"]],
                                            width=-1
                                          )


        dpg.add_separator()

        _name = model_manager.get_group_name(node_id)

        dpg.add_text( "GROUP ", color=ColorPalette.DIM_GRAY )

        with dpg.group( horizontal=True ) :

            dpg.add_combo( items=model_manager.get_group_names(),
                           default_value=_name,
                           tag=str(node_id)+"_combo",
                           callback=group_change_callback,
                           user_data=model_manager
                         )

        with dpg.group( horizontal=True ) :

            dpg.add_text( "Type  ", color=ColorPalette.DIM_GRAY )
            dpg.add_text( default_value=model_manager.get_group_attribute(_name, "type") )

        with dpg.group( horizontal=True ) :

            dpg.add_text( "Color ", color=ColorPalette.DIM_GRAY )
            dpg.add_color_button( default_value=model_manager.get_group_attribute(_name, "color") )


def change_name_callback( sender, app_data, user_data ) :

    """
    called by info window - name
    """

    model_data = user_data[0]
    node_id = user_data[1]
    name = app_data

    # update model
    model_data.set_layer_name( node_id, str(name) )

    # update node
    dpg.configure_item( node_id, label=name )

    # TODO
    # check for type
    print("testets: ", name, dpg.get_item_configuration(node_id)["label"])


def change_param_callback( sender, app_data, user_data ) :

    """
    called by info window - param
    """

    model_data = user_data[0]
    node_id = user_data[1]
    param_name = user_data[2]
    param_type = user_data[3]

    value = app_data

    # update model
    model_data.set_param_value( node_id, param_name, value )

    # updata node
    dpg.configure_item( str(node_id) + "_" + param_name, default_value=value )



# info helper functions

def get_info_item_name( node_id ) :

    return "Layer Attributes_" + str(node_id)

################################### group windows ########################################


def group_editor_callback( sender, app_data, user_data ) :

    """
    called by "group_manager" - buttons (Add, Edit)

     This call the group editor window to show
     If the caller is the button "Add", leave empty field on editor.
     If the caller is the button "Edit", fill the fiels with the group info
     of the group selected on the listbox.
    """

    model_data = user_data

    print("model: ", type(model_data))

    # get selected group
    group_name = get_selected_group_name()

    if dpg.get_item_alias(sender) == group_edit :

        # if the editor not show, unhide it
        if dpg.does_item_exist( group_edit_window_name ) :
            show_editor()

        # if edit mode, prefill the fields with current attributes
        fill_group_editor( model_data, group_name )

    if dpg.get_item_alias(sender) == group_remove :

        if len( model_data.get_group_attribute(group_name, "members") ) == 0 :
            
            # remove empty group
            model_data.remove_group( group_name )

            # update other items related to group
            dpg.configure_item( group_listbox, items=model_data.get_group_names() )
            dpg.configure_item( group_combo_selector_name, items=model_data.get_group_names() )

            # update display
            for selected_node in dpg.get_selected_nodes( node_editor_name ) :
                
                update_node_theme( selected_node, model_data )
                create_display_info( selected_node, model_data, show=True )
    
        else :

            logging.error("Can't remove non-empty group.")



def group_change_callback( sender, app_data, user_data ) :

    """
    called by "group_editor" - buttons OK
    """

    model_data = user_data
    parent = sender

    group_name = get_selected_group_name()

    # if sender is the add button, add directly the new group
    if dpg.get_item_alias(parent) == group_edit_window_name + "_add" :

        print("editor fields: ", pull_editor())
        model_data.add_custom_new_group( *pull_editor() )

    # if sender is the update button, update the existing info
    elif dpg.get_item_alias(parent) == group_edit_window_name + "_update" :
            
            new_name, new_type, new_color = pull_editor()
            
            model_data.change_group_name( group_name, new_name )
            group_name = new_name
            
            model_data.set_group_attribute( group_name, "type", new_type ) 
            model_data.set_group_attribute( group_name, "color", new_color )

    # update other items related to group
    dpg.configure_item( group_listbox, items=model_data.get_group_names() )
    dpg.configure_item( group_combo_selector_name, items=model_data.get_group_names() )
    
    # update display
    for selected_node in dpg.get_selected_nodes( node_editor_name ) :

        update_node_theme( selected_node, model_data )
        create_display_info( selected_node, model_data, show=True )


 
def group_selected_callback( sender, app_data, user_data ) :

    """
    called by "group_grouper" - buttons Yes
    """

    global selected_nodes

    model_data = user_data

    group_name = dpg.get_value( group_combo_selector_name )

    option = dpg.get_item_alias( sender )

    if option == group_yes :

        for node_id in selected_nodes :

            print("selected groups: ", node_id)

            # update group info on model data
            model_data.assign_group( node_id, group_name )

            # update corresponding nodes
            update_node_theme( node_id, model_data )

    if option == group_no :
        dpg.configure_item( group_group_window_name, show=False )

    # clear selected nodes
    selected_nodes.clear()
    
    # hide group window
    hide_group()


""""
"""""""""""""""""""""""""""""""""""""
 helper functions fro group windows
"""""""""""""""""""""""""""""""""""""
"""


# function to fill up editor fields
def fill_group_editor( model_data, group_name=None ) :

    if not group_name :

        group_name = ""

    gtype = model_data.get_group_attribute( group_name, "type" )
    gcolor = model_data.get_group_attribute( group_name, "color" )
    
    #group_name = dpg.get_value("group_listbox")

    if  dpg.does_item_exist(group_edit_window_name) and \
        dpg.is_item_shown(group_edit_window_name) == True :

        dpg.set_value( "input_group_name", group_name )
        dpg.set_value( "input_group_type", gtype )
        dpg.set_value( "group_color_picker", gcolor )


# function to retrieve editor fields' values
def pull_editor() :

    if  dpg.does_item_exist(group_edit_window_name) and \
        dpg.is_item_shown(group_edit_window_name) == True :

        return ( dpg.get_value("input_group_name"), 
                 dpg.get_value("input_group_type"), 
                 dpg.get_value("group_color_picker")
               )


# function to fill up manager fields
def fill_group_manager( model_data ) :

    dpg.configure_item( group_listbox, 
                        items=model_data.get_group_names()
                      )


# function to retrieve manager fields' values 
def get_selected_group_name() :

    return dpg.get_value( group_listbox )


# function to manage group windows appereaces
def show_editor() :

    if not dpg.is_item_shown( group_edit_window_name ) :

        dpg.configure_item( group_edit_window_name, show=True )
        dpg.focus_item( group_edit_window_name )


def show_group() :

    if not dpg.is_item_shown( group_group_window_name ) :

        dpg.configure_item( group_group_window_name, show=True )
        dpg.focus_item( group_group_window_name )


def show_manager() :

    if not dpg.is_item_shown(group_manager_window_name) :

        dpg.configure_item( group_manager_window_name, show=True )
        dpg.focus_item( group_manager_window_name )


def hide_editor() :

    dpg.configure_item( group_edit_window_name, show=False )


def hide_group() :

    dpg.configure_item( group_group_window_name, show=False )


def hide_manager() :

    dpg.configure_item( group_manager_window_name, show=False )



######################################## menubar #########################################


def output_model_callback( sender, app_data, user_data ) :

    # group the layers by group
    model_data = user_data
    model_data.save_model_to_file( 'model_def.json', bygroup=True, cls=SetEncoder )


def output_layers_callback( sender, app_data, user_data ) :

    model_data = user_data
    model_data.save_model_to_file( 'model_layer.json', bygroup=False, cls=SetEncoder )


def output_group_callback( sender, app_data, user_data ) :

    model_data = user_data

    file = 'model_group.json'

    with open(file, 'w', encoding='utf-8') as f :
            
        json.dump( model_data.get_groups(), f, ensure_ascii=False, indent=4, cls=SetEncoder )


def save_callback( sender, app_data, user_data ) :

    model_data = user_data

    file = "project.json"
    model_data.save(file)


def check_model_callback() :
    pass


def save_layout_callback( sender, app_data, user_data ) :

    dpg.save_init_file("./resources/ui_init.ini")



def output_torch_class_callback( sender, app_data, user_data ) :
    
    model_renderer = user_data[0]
    model_data = user_data[1]

    #model_renderer.set_data(model_data.by_group())

    model_renderer.render()


def load_layer_callback( sender, app_data, user_data ) :

    # get current model data
    model_data = user_data

    # clear all items related to current model data
    clear_session( model_data )

    # clear model data
    model_data = {}

    file = "project.json"

    model_data.load(file)

    for layer_id in model_data.keys() :

        add_node( layer_id, model_data )
                            
        update_node_theme( layer_id, model_data )

        # create display on window "layer_info"
        create_display_info( layer_id, model_data )

        # update group list
        dpg.configure_item( "group_listbox", items=model_data.get_group_names() )

        # TODO
        # update links


def load_template_callback( sender, app_data, user_data ) :

    model_renderer = user_data

    def callback( sender, app_data ) :

        model_renderer.set_template_file( app_data["file_name"] )
        dpg.delete_item( "file_dialog_id" )

    def cancel_callback( sender, app_data ):

        dpg.delete_item( "file_dialog_id" )

    with dpg.file_dialog( tag="file_dialog_id",
                          show=True, 
                          callback=callback, 
                          cancel_callback=cancel_callback, 
                          width=700 ,height=400
                        ) :
        
        dpg.add_file_extension( ".j2", color=(0, 255, 0, 255), custom_text="[jinja2]" )


# menu helper functions
        
def clear_session( model_data ) :

    for node_id in model_data.keys() :

        dpg.delete_item( node_id )
        dpg.delete_item( get_info_item_name(node_id) )


# helper to transform set to list since json can't serialize set
class SetEncoder( json.JSONEncoder ) :

    def default( self, obj ) :

        if isinstance( obj, set ) :

            return list( obj )
        
        return json.JSONEncoder.default( self, obj )