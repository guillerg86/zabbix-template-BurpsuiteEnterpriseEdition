###################################################################################################
# Modulo con las funciones para gestionar usuarios con la API de Burpsuite Enterprise Edition
# @author: Guille Rodríguez González - https://www.linkedin.com/in/guille-rodriguez-gonzalez/
# @version: 2024.07.03
# @api_version: For GraphQL API V1
###################################################################################################

import requests
import json


class BurpsuiteEnterpriseEdition(object):
    def __init__(self,api_token=None, api_base_url=None, ssl_verify=True):
        self.__session = requests.Session()
        self.__session.headers = {"Content-Type": "application/json", "Authorization": api_token }
        self.__session.verify = ssl_verify
        self.__api_base_url = api_base_url
        self.__ssl_verify = ssl_verify
    
        if self.__ssl_verify == False:
            requests.packages.urllib3.disable_warnings()
    ###############################################################################################
    # API QUERY METHODS
    # This methods are helper methods for return queries or vars setted to send to API in the requests
    ###############################################################################################
    def __query_GetAgentPools(self):
        return '''
            query GetAgentPools {
                agent_pools {
                    id
                    name
                    description
                    agents {
                        id
                        name
                    }
                    sites {
                        id
                    }
                }
            }
        '''
    
    def __variable_GetAgent(self,agent_id):
        return {"id":agent_id}

    def __query_GetAgent(self):
        return '''
            query agent($id: ID!) {
            agent(id: $id) {
                id
                name
                current_scan_count
                ip
                state
                error {
                code
                error
                }
                enabled
                max_concurrent_scans
                cpu_cores
                system_ram_gb
                warning
            }
            }
        '''


    ###############################################################################################
    # API METHODS
    ###############################################################################################
    def get_agent(self,agent_id=None):
        data = { 'query': self.__query_GetAgent(), "variables" : self.__variable_GetAgent(agent_id) }
        response = self.__session.post(self.__api_base_url,json=data)
        response.raise_for_status()
        resp_json = json.loads(response.text)
        if resp_json.get('errors',None):
            for data in resp_json['errors']:
                if "agent not found" == data['message'].lower().strip():
                    raise requests.exceptions.HTTPError(f"HTTP 404 - {data['message']}")
            raise Exception(resp_json)
        return resp_json['data']['agent']


    def get_agent_pool(self):
        data = { 'query': self.__query_GetAgentPools() }
        response = self.__session.post(self.__api_base_url,json=data)
        response.raise_for_status()
        resp_json = json.loads(response.text)

        return resp_json['data']['agent_pools']


    ###############################################################################################
    # CUSTOM METHODS
    ###############################################################################################
    def get_all_agents(self):
        agents = []
        for pool in self.get_agent_pool():
            for agent in pool['agents']:
                agent = self.get_agent(agent_id=agent['id'])
                agent['pool'] = {'id':pool['id'],'name':pool['name'],'description':pool['description']}
                agents.append(agent)
        return agents
        
    