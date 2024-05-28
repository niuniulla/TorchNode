import json, copy
import logging
from .theme import ColorPalette

############################
# the model data structure #
############################

# layer_name
#  |
#  |-- type:        type of layer - "type" in layers_definition.json
#  |
#  |-- category:    category of the type - key under torch.nn in layers_definition.json
#  |
#  |-- description: description of the layer
#  |
#  |-- input:       number of inputs
#  |
#  |-- output:      number of outputs
#  |
#  |-- name:        name of the layer in model - name of the class member in torch modle class
#  |
#  |-- id:          unique id of the layer, assigned using UI
#  |
#  |-- group:       the assigned group name - the class
#  |
#  |-- link_start : list of input nodes
#  |
#  |-- link_end:    list of output nodes
#  |
#  |-- parameters:  list of parameters
#       |
#       |-- name:           name of the parameters (eg. in_channels for conv2d)
#       |
#       |-- dtype:          data type (eg. int)
#       |
#       |-- description: 
#       |
#       |-- default_value:
#       |
#       |-- value:
#       |
#       |-- default:        to indicate if it is default


#######################
# the group structure #
#######################

# group_name
#  |
#  |-- name:        unique name of the group
#  |
#  |-- color:       the color to be used to colorize the nodes
#  |
#  |-- type:        can be class, sequential, modulelist
#  |
#  |-- members:     list of node id assigined to this group


class ModelManager() :

    def __init__( self, file ) :

        self.label = "model_manager"
        self.file = file

        with open(file) as f:
            self.data = json.load(f)

        self.model_data = {}
        self.layer_type = {}
        self.layer_data = {}
        self.layer_category = {i:0 for i in self.data["torch.nn"]}

        self.groups = {}

        for l in self.layer_category :

            self.layer_data[l] = []

            for k in self.data["torch.nn"][l] :

                self.layer_data[l].append(k)
                self.layer_type[k["type"]] = 0


    # remove all data related to a layer
    def remove_layer( self, layer_id ) :

        # remove from the layer type count
        self.layer_type[self.model_data[layer_id]["type"]] -= 1

        self.model_data.pop(layer_id)


    # add a layer
    def add_layer( self, layer_id, layer_info ) :

        self.model_data[layer_id] = copy.deepcopy( layer_info )

        self.model_data[layer_id]["name"] = layer_info["type"] + "_"
        self.model_data[layer_id]["name"] += str(self.layer_type[layer_info["type"]])

        self.layer_type[layer_info["type"]] += 1

        self.model_data[layer_id]["link_start"] = set() # no link
        self.model_data[layer_id]["link_end"] = set() # no link

        self.model_data[layer_id]["id"] = layer_id

        self.model_data[layer_id]["pos"] = [-1, -1] # no pos

        self.assign_group( layer_id, None )


    # add a layer by name
    def add_layer_from_data( self, layer_id, layer_name ) :

        self.model_data[layer_id] = copy.deepcopy( self.data[layer_name] )
        
        self.model_data[layer_id]["name"] = layer_name

        if self.layer_type[layer_name] > 0:

            self.model_data[layer_id]["name"] += str(self.layer_type[self.model_data[layer_id]["name"]])

        self.layer_type[layer_name] += 1

        self.model_data[layer_id]["link_start"] = set() # no link
        self.model_data[layer_id]["link_end"] = set() # no link

        self.model_data[layer_id]["id"] = layer_id

        self.assign_group( layer_id, None )


    # set a layer's name
    def set_layer_name( self, layer_id, name ) :

        self.model_data[layer_id]["name"] = name


    # return a layer's name by its ID
    def get_layer_name( self, layer_id ) :

        return self.model_data[layer_id]["name"]
    

    # set position
    def set_layer_pos( self, layer_id, pos ) :

        self.model_data[layer_id]["pos"] = list(pos)
    

    # return the layer node position
    def get_layer_pos( self, layer_id ) :

        return list(self.model_data[layer_id]["pos"])
    

    # return the type of a layer
    def get_layer_type( self, layer_id ) :

        return str(self.model_data[layer_id]["type"])
    

    # change a layer's parameter by its name
    def set_param_value( self, layer_id, param_name, value ) :

        try :

            i = self.get_params_names(layer_id)[param_name]
            self.model_data[layer_id]["parameters"][i]["value"] = value

        except ValueError :

            print("Invalid value.")


    # return a layer's parameter's value
    def get_param_value( self, layer_id, param_name ) :
            
        i = self.get_params_names(layer_id)[param_name]

        return self.model_data[layer_id]["parameters"][i]["value"]


    # return a layer's all parameter names
    def get_params_names( self, layer_id ) :

        return {p["name"]:i for i, p in enumerate(self.model_data[layer_id]["parameters"])}
    

    # return a layer's parameter dict (key, value)
    def get_params( self, layer_id ) :

        return self.model_data[layer_id]["parameters"]


    # return the number of parameters of a layer
    def count_params( self, layer_id ) :

        return len(self.get_params_names(layer_id))


    # set the linked nodes's ID by position
    def assign_link( self, layer_id, alayer_id, before=True ) :

        if before :

            self.model_data[layer_id]["link_start"].add(alayer_id)

        else :

            self.model_data[layer_id]["link_end"].add(alayer_id)

    
    #  set the linked nodes's ID 
    def assign_links( self, layer_id, alayer_ids ) :

        self.model_data[layer_id]["link_start"].add(alayer_ids[0])
        self.model_data[layer_id]["link_end"].add(alayer_ids[1])


    # remove the linked node by position (before, after)
    def remove_link( self, layer_id, alayer_id, before=True ) :

        if before :

            self.model_data[layer_id]["link_start"].remove(alayer_id)

        else :

            self.model_data[layer_id]["link_end"].remove(alayer_id)

    
    # remove linked nodes
    def remove_links( self, layer_id, alayer_ids ) :

        self.model_data[layer_id]["link_start"].remove(alayer_ids[0])
        self.model_data[layer_id]["link_end"].remove(alayer_ids[1])


    # remove all linked nodes
    def remove_links( self, layer_id, alayer_ids ) :

        self.model_data[layer_id]["link_start"].clear()
        self.model_data[layer_id]["link_end"].clear()


    # remove corresponding linked nodes 
    def remove_mutual_links( self, layer_id1, layer_id2 ) :

        if layer_id1 in self.model_data[layer_id2]["link_start"] :

            self.model_data[layer_id1]["link_end"].remove(layer_id2)
            self.model_data[layer_id2]["link_start"].remove(layer_id1)

        if layer_id2 in self.model_data[layer_id1]["link_start"] :

            self.model_data[layer_id2]["link_end"].remove(layer_id1)
            self.model_data[layer_id1]["link_start"].remove(layer_id2)
        

    # return the linked nodes
    def get_links( self, layer_id ) :

        return self.model_data[layer_id]["link_start"], self.model_data[layer_id]["link_end"]


    # return all added layers
    def count_all_layers( self ) :

        return len(self.model_data)
    

    # return all layers' ID
    def get_all_layer_ids( self ) :

        return self.model_data.keys()


    # print a layer's info
    def show_layer( self, layer_id ) :

        print(self.model_data[layer_id])


    # print all added layers' info
    def show_all_layers( self ) :

        for k, l in self.model_data.items() :

            print(l)


    # return the number od all groups
    def count_all_groups( self ) :

        return len(self.get_group_names())


    # count number of added layers by type
    def update_type_count( self, layer_name ) :

        self.layer_type[self.layer_info[layer_name]] += 1


    # save model to file
    def save_model_to_file( self, file, bygroup=True, cls=None ) :

        if bygroup :

            model = self.by_group()

        else:

            model = self.model_data

        with open(file, 'w', encoding='utf-8') as f :

            if not cls :
                json.dump( model, f, ensure_ascii=False, indent=4 )

            else : 

                json.dump( model, f, ensure_ascii=False, indent=4, cls=cls )
    

    # add a group by default
    def add_default_node_group( self, layer_id ) :

        """
        The default group name is constructed by a layer's ID
        """

        group_name = "group_" + str(layer_id)

        if ( group_name in self.groups.keys() ) :

            logging.warning("Group name already exists.")
            return

        self.groups[group_name] = {}

        # set type
        self.groups[group_name] |= {"type": "default"}

        # set random color
        color = ColorPalette.random_color()
        # while color in self.groups.values()["color"]:
        #     color = ColorPalette.random_color()
        self.groups[group_name] |= {"color" : color}

        # init list
        self.groups[group_name] |= {"members" : set()}

        return group_name


    # add a new group by name
    def add_custom_new_group( self, _name, dtype="default", color=None ) :

        if _name in self.groups :

            logging.warning("Group name already exists.")
            return
        
        if _name == "" :

            logging.warning("Enter a valid name.")
            return
        
        if color is not None :

            if len(color) > 3 :

                color = color[0:3]

            if type(color[0]) is not int :

                color = [int(i) for i in color]

            if color in self.groups.values() :

                logging.warning("Color already exists.")
                return
        
        if color is None :

            color = ColorPalette.random_color()

            while color in self.groups.values() :

                color = ColorPalette.random_color() 

        self.groups[_name] = {}
        self.groups[_name]["color"] = color
        self.groups[_name]["type"] = dtype
        self.groups[_name]["members"] = set()
        
        print(self.groups)

    
    # assign a group to a layer
    def assign_group( self, layer_id, group_name=None ) :
        
        if group_name is None :

            group_name = "group_" + str(layer_id)

            if not group_name in self.groups.keys() :

                group_name = self.add_default_node_group( layer_id )
                self.model_data[layer_id]["group"] = group_name
                self.groups[group_name]["members"].add(layer_id)

                return
            
        elif group_name in self.get_group_names() :

            old_group = self.model_data[layer_id]["group"]

            # if the same, do nothing
            if group_name == old_group :

                return

            # remove from old group
            print("remove old group: ", old_group)
            print("old group members: ", self.get_group_attribute(old_group, "members"))

            if  old_group in self.get_group_names() :

                if layer_id in self.get_group_attribute(old_group, "members") :

                    self.groups[old_group]["members"] = [i for i in self.groups[old_group]["members"] if i != layer_id]
                    print("new members: ", self.groups[old_group]["members"])

            # set new group
            self.model_data[layer_id]["group"] = group_name
            self.groups[group_name]["members"].add(layer_id)
            return
        
        else:

            logging.warning("Group not exist.")


    # return the member group
    def get_groups( self ) :

        return self.groups


    # change a group's name
    def change_group_name( self, old_name, new_name ) :

        if (old_name in self.groups.keys()) and not (new_name in self.groups.keys()) :

            self.groups[new_name] = self.groups.pop(old_name)

        else :

            logging.warning("name not found or new name already used")


    # change a group's attributes
    def set_group_attribute( self, group_name, attr, value ) :

        self.groups[group_name][attr] = value


    # return a group's attributes
    def get_group_attribute( self, group_name, attr ) :

        if group_name in self.groups.keys() :

            return self.groups[group_name][attr]
        
        else :

            return ""
    
    
    # return all groups' name
    def get_group_names( self ) :

        return list(self.groups.keys())



    # helper function 
    def return_random_color( self ) :
        
        return ColorPalette.random_color()
  
    
    # return the group name of a layer
    def get_group_name( self, layer_id ) :

        return self.model_data[layer_id]["group"]
    
    # remove group by name
    def remove_group( self, name ) :

        if name in self.groups.keys() :

            self.groups.pop(name)

    
    # get number of input
    def get_count_input( self, layer_id ) :

        return int(self.model_data[layer_id]["input"])
            

    # get number of input
    def get_count_output( self, layer_id ) :

        return int(self.model_data[layer_id]["output"])
            

    # save all
    def save( self, file, cls=None ) :

        data = {}
        data["model_data"] = self.model_data
        data["groups"] = self.groups
        data["layer_type"] = self.layer_type
        data["layer_data"] = self.layer_data
        data["layer_category"] = self.layer_category

        with open(file, 'w', encoding='utf-8') as f :

            if not cls :

                json.dump(data, f, ensure_ascii=False, indent=4)

            else : 

                json.dump(data, f, ensure_ascii=False, indent=4, cls=cls)


    def load( self, file ) :

        with open(file) as f :

            data = json.load(f)

        self.model_data = data["model_data"]
        self.groups = data["groups"]
        self.layer_type = data["layer_type"]
        self.layer_data = data["layer_data"]
        self.layer_category = data["layer_category"]

        # TODO
        # set some list to set

    
    # rearrange layers by group
    def by_group( self ) :

        """
        To rearrage the dict by group, in order to generate
        model files
        """

        model_rearranged = {}

        for g in self.get_group_names() :

            model_rearranged[g] = {}

        for k, l in self.model_data.items() :

            group_name = l["group"]
            model_rearranged[group_name].update({k: l})

        # chack empty group
            
        # chack no default parameters no empty
            
        # check links

        return model_rearranged
    

    # find the beginning nodes of a group
    def find_start_nodes( self, group ) :

        if not group in self.get_group_names() :
             
             logging.warning("Group not exist")
             return
        
        starts = []
        
        all_layers_in_group = self.groups[group]["members"]

        print("all_nodes: ", all_layers_in_group)
        
        for layer_id in all_layers_in_group :

            linked_nodes = self.model_data[layer_id]["link_start"]

            if len(linked_nodes) == 0 :
                
                starts.append(layer_id)

        return starts
    

    # find the ending nodes of a group
    def find_end_nodes( self, group ) :

        if not group in self.get_group_names() :
             
             logging.warning("Group not exist")
             return
        
        ends = []
        
        all_layers_in_group = self.groups[group]["members"]
        
        for layer_id in all_layers_in_group :

            linked_nodes = self.model_data[layer_id]["link_end"]

            if len(linked_nodes) == 0 :
                
                ends.append( layer_id )

        return ends
    

    # find paths
    def bfs( self, group ) :

        ordered_nodes = []
        paths = []

        nodes_undone = {}
        nodes_done = []

        start_nodes = self.find_start_nodes( group )
        print("start_nodes: ", start_nodes)

        end_nodes = self.find_end_nodes( group )
        print("end_nodes: ", end_nodes)

        for node in start_nodes :

            nodes_done.append( node )

        

        while True :

            current_node = nodes_done.pop(-1)
            ordered_nodes.append(current_node)

            # add all children to the list
            for child in self.model_data[current_node]["link_end"] :

                if child in nodes_undone.keys() :

                    nodes_undone[child] += 1

                else :

                    nodes_undone.update({child:1})

            # treat nodes with all inputs
            temp_nodes = []
            print("undone: ", nodes_undone)

            for node in nodes_undone.keys() :

                # all inputs satisfied
                if nodes_undone[node] == len(self.model_data[node]["link_start"]) :

                    temp_nodes.append( node )
                    #ordered_nodes.append(node)

                    # TODO
                    # done_nodes
                    nodes_done.append( node )

                # if reach the end, get the path
                if node in end_nodes :

                    end_node = node

                    # get the path
                    print("ordered nodes: ", ordered_nodes)

                    path = [end_node]
                    temp_ordered_nodes = ordered_nodes
                    temp_ordered_nodes.reverse()

                    print("temp ordered nodes: ", temp_ordered_nodes)

                    for prev_node in temp_ordered_nodes :

                        if prev_node in self.model_data[end_node]["link_start"] :

                            path.append( prev_node )
                            end_node = prev_node

                    path.reverse()
                    paths.append( path )

            # update undone nodes
            print("temp nodes: ", temp_nodes, nodes_undone)

            for node in temp_nodes :
                
                nodes_undone.pop( node )

            # no more nodes, so quit
            if not nodes_done :
                break

        print("paths: ", paths)
        return paths

                
    def bfs_group( self ) :

        group_path = []

        for group in self.groups :

            start = self.find_start_nodes( group )

            if start in input :
                group_path.append( group )
                break

        while False :

            last = self.find_last_nodes(group_path[-1])
            group_path.append(self.model_data[last]["link_end"][-1]) # suppose there is only one last node

        return group_path