import yaml
import config
from pyzabbix import ZabbixAPI

zapi = ZabbixAPI(config.url)
zapi.login(config.user, config.password)

cfg = yaml.load(open(config.file))

urls = {i['name']: i for i in cfg}

zbx_hosts_ids = []
for host in config.zbx_hosts:
    host_id = zapi.host.get(output="hostid", filter={"host": host})[0]['hostid']
    if host_id not in zbx_hosts_ids:
        zbx_hosts_ids.append(host_id)


def delete_checks():
    z_urls = []

    for check in zapi.httptest.get(selectSteps="extend", hostids=zbx_hosts_ids):
        url = check.get('name')
        host_id = check.get('hostid')
        z_urls.append(url)

        if url not in urls.keys():
            # Delete http check, if it exists in Zabbix, but doesn't exist in file
            httptest_id = zapi.httptest.get(selectSteps="extend",
                                            hostids=host_id,
                                            filter={"name": url})[0]["httptestid"]
            zapi.httptest.delete(httptest_id)
            print("Httpcheck {} deleted".format(url))
        else:
            print("Nothing to do")


def check_url():
    z_urls = []
    for check in zapi.httptest.get(selectSteps="extend", hostids=zbx_hosts_ids):
        url = check.get('name')
        z_urls.append(url)

    already = True

    for line in urls:
        env = urls.get(line).get('env')
        name = urls.get(line).get('name')
        url = urls.get(line).get('url')
        priority = urls.get(line).get('priority')
        host_id = zapi.host.get(output="hostid",
                                filter={"host": env})[0]['hostid']

        if urls.get(line).get('delay'):
            delay = int(urls.get(line).get('delay'))
        else:
            delay = 60

        if urls.get(line).get('retries'):
            retries = int(urls.get(line).get('retries'))
        else:
            retries = 1

        if urls.get(line).get('timeout'):
            timeout = int(urls.get(line).get('timeout'))
        else:
            timeout = 15

        if urls.get(line).get('headers'):
            headers = (urls.get(line).get('headers'))
        else:
            headers = ""

        if line in z_urls:
            print('Already added: {}'.format(line))
            info = zapi.httptest.get(selectSteps="extend",
                                     hostids=host_id,
                                     filter={"name": line})[0]

            # Update checks and triggers from file
            zapi.httptest.update(httptestid=info.get('httptestid'),
                                 # name=name,
                                 delay=delay,
                                 retries=retries,
                                 headers=headers,
                                 steps=[{'httpstepid': info.get('steps', [{}])[0].get('httpstepid'), "name": name,
                                         "url": url, "status_codes": 200, "no": 1, "timeout": timeout}])

        else:
            already = False
            print("Add httpcheck and trigger for: {}".format(line))

            # Create web-check
            zapi.httptest.create(name=name,
                                 hostid=host_id,
                                 delay=delay,
                                 retries=retries,
                                 headers=headers,
                                 steps=[{"name": name, "url": url, "status_codes": 200, "no": 1, "timeout": timeout}])

            # Create triggers on this webchecks
            zapi.trigger.create(description="No response from {}".format(name),
                                priority=priority,
                                comments="Проблемы с сервисом {}. Смотрите HTTP код ручки в Last Value".format(name),
                                expression="{%s:web.test.rspcode[%s,%s].last()}<199 or"
                                           " {%s:web.test.rspcode[%s,%s].last()}>399" % (
                                    env, name, name, env, name, name
                                ))

    if already:
        print("Done")
delete_checks()
check_url()
