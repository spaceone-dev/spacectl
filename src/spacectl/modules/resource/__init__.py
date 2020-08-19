from spacectl.command.execute import _check_api_permissions, _get_service_and_resource, _get_client,_call_api, _parse_parameter
from spacectl.lib.output import print_data
from spacectl.conf.global_conf import RESOURCE_ALIAS, EXCLUDE_APIS, DEFAULT_PARSER
from spacectl.conf.my_conf import get_config, get_endpoint, get_template


def apply(task):
    # spaceone api 실행

    service, resource = task.spec["resource_type"].split(".")

    read_params = {match: task.spec["data"][match] for match in task.spec["matches"]}
    read_resources = []
    if task.spec["verb"]["read"]:
        try:

            verb = task.spec["verb"]["read"]
            # list를 지원안하면 exception
            read_resources = __execute_api(service, resource, verb, read_params, api_version="v1", output="yaml", parser={})
            if isinstance(read_resources, list):
                task.output = read_resources[0]
            else:  # like dict
                task.output = read_resources
        except Exception as e:
            print(e)
            read_resources = []
    print("### Read Result ###")
    print(read_resources)
    params = {key: value for key, value in task.spec["data"].items()}

    if len(read_resources) == 1 and task.spec["verb"]["update"]:
        try:
            verb = task.spec["verb"]["update"]
            print("Start", ".".join([service, resource, verb]))
            _check_api_permissions(service, resource, verb)
            update_result = __execute_api(service, resource, verb, params, api_version="v1", output="yaml", parser={})
            print("Finish", ".".join([service, resource, verb]))
            task.output = update_result
        except Exception as e:
            print(e)
            print("Unavailable update field so Skip", ".".join([service, resource, "update"]))
            task.output = read_resources[0]

    elif len(read_resources) == 0 and task.spec["verb"]["create"]:
        verb = task.spec["verb"]["create"]
        print("Start", ".".join([service, resource, verb]))
        print(params)
        create_result = __execute_api(service, resource, verb, params, api_version="v1", output="yaml", parser={})
        print("Finished", ".".join([service, resource, verb]))
        task.output = create_result
    else:
        print("No Create or Update on", task)
    print("### Output ###")
    print(task.output)
    print("\n")


def __execute_api(service, resource, verb, params={}, api_version='v1', output='yaml', parser=None):
    config = get_config()
    _check_api_permissions(service, resource, verb)
    client = _get_client(service, api_version)

    response = _call_api(client, resource, verb, params, config=config)

    if verb == 'list':
        results = response.get('results', [])
        if len(results) == 0:
            return []
        elif len(results) > 1:
            Exception()
        else:
            return results
    elif verb == 'get':
        return response
    elif verb == 'create':
        return response
    elif verb == 'update':
        return response
    else:
        print("Unknown verb", verb)
        return response