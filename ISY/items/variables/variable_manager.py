#! /usr/bin/env python
import xml.etree.ElementTree as ET

from .. item_manager import Item_Manager
from .variable_info import Variable_Info
from .variable_name import Variable_Name
from .variable_integer import Variable_Integer
from .variable_state import Variable_State

import logging
logger = logging.getLogger(__name__)

variable_classes = {
    '1' : Variable_Integer,
    '2' : Variable_State,
}

class Variable_Manager (Item_Manager):

    def __init__(self, controller):
        Item_Manager.__init__(self,controller,'Variable')

    def start(self):
        success = True

        variable_list_response = self.controller.send_request('vars/get/1') # get integer vars
        variable_name_response = self.controller.send_request('vars/definitions/1') # get integer vars

        if variable_list_response.status_code == 200 and variable_name_response.status_code == 200:
            list_root = ET.fromstring (variable_list_response.content)        
            name_root = ET.fromstring (variable_name_response.content)        
            self.process_variable_nodes (list_root,name_root)       
        else:
            success = False

        variable_list_response = self.controller.send_request('vars/get/2') # get state vars
        variable_name_response = self.controller.send_request('vars/definitions/2') # get state vars

        if variable_list_response.status_code == 200 and variable_name_response.status_code == 200:
            list_root = ET.fromstring (variable_list_response.content)        
            name_root = ET.fromstring (variable_name_response.content)        
            self.process_variable_nodes (list_root,name_root)       
        else:
            success = False

    def process_variable_nodes(self,list_root,name_root):
        for node in list_root.iter('var'):
            variable_info = Variable_Info(node)

            if variable_info.valid: # make sure we have the info we need
                variable_class = variable_classes [variable_info.type]
                variable = variable_class(self,variable_info)

                #find name
                for node in name_root.iter('e'):
                    variable_name = Variable_Name (node)

                    if variable_name.valid and variable_name.id == variable.id:
                        variable.name = variable_name.name

                self.add(variable,variable.get_index())
         
    def websocket_event(self,event):
        var = event.event_info_node.find('var')
        variable_id = var.attrib ['id']
        variable_type = var.attrib ['type']

        index = variable_type+':'+variable_id

        variable = self.get(index)
        variable.process_websocket_event(event)

