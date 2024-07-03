############################################################################################
# Script para extraer el estado de las sondas a través de la API, generando un JSON como resultado
# @author: Guille Rodríguez González 
# @version: 2024.07.03
###################################################################################################
from burpsuiteee import BurpsuiteEnterpriseEdition
from dotenv import dotenv_values
from requests.exceptions import HTTPError
import argparse
import json



def configure_parser():
    parser = argparse.ArgumentParser(
        prog="Burpsuite Enterprise Edition Scan Resources Checker", 
        description="Get the info from the Burpsuite Enterprise Edition server via API"
    )
    
    parser.add_argument("--api-token",required=True)
    parser.add_argument("--api-base-url",required=True)
    parser.add_argument("--disable-ssl-verify",action='store_true')
    parser.add_argument("--action",choices=["discover","agentinfo"],required=True)
    parser.add_argument("--agent-id",required=False,type=int)
    args = parser.parse_args()
    return args


if __name__ == "__main__":    
    args = configure_parser()
    
    config = {
        "API_BASEURL": args.api_base_url, 
        "API_TOKEN":args.api_token
    }
    
    ssl_verify = not args.disable_ssl_verify
    api = BurpsuiteEnterpriseEdition(api_base_url=config["API_BASEURL"],
                                     api_token=config["API_TOKEN"],
                                     ssl_verify=(not args.disable_ssl_verify))

    
    if args.action == "discover":
        print(json.dumps(api.get_all_agents()))
        exit(0)
    
    if args.action == "agentinfo":
        if args.agent_id is None or args.agent_id <= 0:
            print("AgentID can't be empty, zero or less than 0")
            exit(-1)
        try:
            print(json.dumps(api.get_agent(agent_id=args.agent_id)))
        except HTTPError as httpe:
            print(str(httpe))
        except Exception as e:
            print(str(e))