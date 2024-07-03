# BurpsuiteEnterpriseEdition Zabbix Template

Script para poder monitorizar el estado de los agentes de BurpsuiteEnterpriseEdition

## Motivación

Por lo general se miraria si el servicio `burpsuiteenterpriseedition_agent.service` está encendido. Sin embargo he detectado que muchas veces en la consola indica que la sonda/agente está Desconectado y al realizar un 

```
systemctl status burpsuiteenterpriseedition_agent.service
```

devuelve resultado running. Procediendo a revisar el log

```
tail -f /var/log/BurpSuiteEnterpriseEdition/supervisor_enterpriseAgent.log
```

En vez de aparecer logs normales, aparecen mensajes de error. Algunos como ClassNotFoundException... obviamente ni reiniciar el servicio ni reiniciar el sistema operativo hicieron que funcionara. Solo la reinstalación de la sonda/agente.
Sin embargo esto ya indica que uno no se puede fiar del servicio `burpsuiteenterpriseedition_agent.service` ya que pese a los fallos indica que esta running.

Por ello creo que es mas fiable monitorizar el estado de las sondas/agentes desde el punto de vista de el servidor. Para ello he creado dos scripts

## Ficheros

### burpsuiteee.py

Es una clase DAO para facilitar la comunicación con la API de Burpsuite Enterprise Edition

### burpsuiteee_monitor_agents.py 

Dispone de dos funciones. 

- [x] Discover: Extrae un JSON con todos los agentes que hay en la consola y su estado. Esto permitirá a Zabbix hacer una Discovery Rule
- [x] Agentinfo: Si se le envia la ID de la sonda, obtiene la información de esta y lo devuelve tambien en formato JSON. Permitirá a Zabbix crear un raw item prototype por cada una de las sondas y luego dependant items para cada dato del json. 

### Template Burpsuite Enterprise Edition

Template Zabbix Agent Active comprobado y creado en la versión 7.0 LTS de Zabbix, pero debería ser compatible almenos con la version 6.X


## Requisitos

- [x] Python3 instalado en el sistema (comprobado con la 3.12)
- [x] Librería Requests (`pip install requests`)

## Probar el funcionamiento

Ejecute el siguiente comando

```
python3.exe burpsuiteee_monitor_agents.py --disable-ssl-verify --api-token TOKEN_API --api_base-url https://burpsuiteserver.yourdomain.tld/graphql/v1 --action discover
```

Si todo es correcto, recibirá un json como respuesta, con identificadores de los agentes, lance la siguiente ejecución cambiando ID_AGENTE por el id de uno de los que haya salido en el resultado

```
python3.exe burpsuiteee_monitor_agents.py --disable-ssl-verify --api-token TOKEN_API --api_base-url https://burpsuiteserver.yourdomain.tld/graphql/v1 --action discover --action agentinfo --agent-id ID_AGENTE
```

## Instalación

Actualmente se usa un agente, ya que la idea es usar el agente que tiene el propio servidor instalado. Aunque al ser consultado via API se podría modificar para que se ejecutará mediante el Zabbix server / proxy

Por ello en el agente se han de crear un fichero de configuración con los UserParameter.

**Linux**

```
UserParameter=burpsuiteee.scanresources.discover[*],/usr/bin/python3 /etc/zabbix/scripts/burpsuiteee_monitor_agents.py --disable-ssl-verify --api-token $1 --api-base-url $2 --action discover
UserParameter=burpsuiteee.scanresources.agentinfo[*],/usr/bin/python3 /etc/zabbix/scripts/burpsuiteee_monitor_agents.py --disable-ssl-verify --api-token $1 --api-base-url $2 --action agentinfo --agent-id $3
```

Si desea forzar la comprobación de certificado SSL del servidor en la petición, borre el `--disable-ssl-verify`. Guarde los cambios.

Cree una carpeta llamada scripts en el directorio de zabbix

```
mkdir /etc/zabbix/scripts
```

Copie los ficheros burpsuiteee.py y burpsuiteee_monitor_agents.py 

```
cp burpsuiteee.py /etc/zabbix/scripts
cp burpsuiteee_monitor_agents.py /etc/zabbix/scripts
```
### Prototype Items

- Identifier
- Name
- IP Address
- Current scan count
- Max concurrent scans
- CPU Cores
- RAM (GB)
- State
- Warning
- Error
- Enabled

### Prototype Triggers

|Trigger|Severity|Condition|
|-|-|-|
|Scanner {#NAME} has warnings|Warning|Cuando warning sea diferente de null|
|Scanner {#NAME} is disconnected|Disaster|Cuando state sea DisconnectedState|
|Scanner {#NAME} not authorized|Warning|Cuando state no sea AuthorizedState y tampoco sea DisconnectedState|
|Scanner {#NAME} with error|Disaster|Cuando error sea diferente de null| 

## Error

### HTTP 404 - Agent not found

Este mensaje aparecerá cuando se consulte un identificador de agente que ya no exista en el servidor. Ejecute discover para visualizar cuales son los correctos