# zabbix-httpcheck
zabbix-httpcheck is Python script which controls Zabbix http tests from yaml file. Create/update/delete http tests and triggers for them.

## Requirements: 
* python >= 3.4
* python libs: pyzabbix, pyyaml

## Installation: 
1. Clone repo: https://github.com/OSidorenkov/zabbix-httpcheck.git
2. Create and configure `config.py` near httpcheck.py. You can take as an example `config.py.example` from repo.
3. Install python libs: `pip3 install pyzabbix pyyaml`

## Configuration:  
1. Create fake host or hosts in Zabbix where you want to see the Web checks, for example:  
* dev
* qa
* stage
* prod

2. Edit `config.py`, paste your hosts for web checks into the list `zbx_hosts`.

## Usage:
In order to add new web services addresses to monitoring, you need:
* Add to the file `httpcheck.yaml` information about the web check, for example:

```yaml
- name: GitHub
  url: https://github.com/OSidorenkov
  env: prod
  priority: 4
```

### Required parameters

* `name` - name of web check
* `url` - web check address
* `env` - service environment
* `priority` - importance of web check, where
	* 1 - information
	* 2 - warning
	* 3 - average
	* 4 - high
	* 5 - disaster

### Extra options

You can also customize your validation by adding the following parameters:

* `delay` - Execution interval of the web scenario in seconds. Default: 60.
* `retries` - Number of times a web scenario will try to execute each step before failing. Default: 1.
* `timeout` - Request timeout in seconds. Default: 15.
* `headers` - HTTP headers that will be sent when performing a request. Scenario step headers will overwrite headers specified for the web scenario.

Example:  

```yaml
- name: GitHub
  url: https://github.com/OSidorenkov
  env: qa
  priority: 2
  delay: 120
  timeout: 30
  retries: 3
  headers: "Accept: application/json"
```

### Update and delete

It is allowed to update existing web checks by changing or adding the following parameters:  

* *url*
* *delay*
* *timeout*
* *retries*
* *headers*

To delete a Web check, remove this check from the file and push it into the repository.
Do not try to change the name of the verification (`name`). This will result in the old checkout being deleted and creating a new one, losing the history.

### Execute

Go to the script directory and run:  
`python3 httpcheck.py`

The script will check that you need to create, update or delete and perform all actions. Like that: 

* Web scenario:  

<img width="811" alt="2017-07-20 15 27 01" src="https://user-images.githubusercontent.com/12871885/28417281-3503c1cc-6d60-11e7-997d-011687400a3b.png">


* Steps:

<img width="929" alt="2017-07-20 15 27 20" src="https://user-images.githubusercontent.com/12871885/28417312-575e5bf6-6d60-11e7-917e-c34642f1bb59.png">


* Trigger:

<img width="752" alt="2017-07-20 15 28 46" src="https://user-images.githubusercontent.com/12871885/28417349-849bd62a-6d60-11e7-888c-6fbda2fd21e5.png">


