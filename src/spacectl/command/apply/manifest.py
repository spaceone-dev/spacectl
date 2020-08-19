import yaml
from spacectl.command.apply.task import Task, TaskList
from spacectl.modules.resource.resource_task import ResourceTask
from spacectl.modules.shell.shell_task import ShellTask
class Manifest:

    def __init__(self, manifest_dict):

        self._dict = manifest_dict
        self.env = manifest_dict["env"]
        self.var = manifest_dict["var"]
        self.tasks = TaskList()

        for task_dict in manifest_dict["tasks"]:
            module = task_dict["uses"].split("/")[-1]
            task = None
            if module == "resource":
                task = ResourceTask(self, task_dict)
            elif module == "shell":
                task = ShellTask(self, task_dict)
            self.tasks.append(task)

        '''
        vars 오버라이딩, 설정
        envs 오버라이딩, 설정
        spaceone context를 설정
        syntax.read_yaml을 통해 yaml 우리의 로직에 맞게 validate 후 yaml_dict에 넣음
        yaml dict를 통해
        env, vars 설정 및 오버라이딩되기로해서 무시해야할 변수들 무시

        self.yaml_dict["resoruces"] 이용해 Resource 생성
        '''

    def execute_expression(self, expression):
        # self 의 attr을 local var로
        resources = self.resources
        var = self.var
        env = self.env
        spaceone = self.spaceone

        result = eval(expression)
        if str(result).startswith("$"):
            # 만약에 찾아간 value가 또 어떤 resource의 지역 expression이라면 걔의 get value 호출
            return self.execute_expression(result)
        else:
            return result
