

class Operator:

    downstream_tasks = []
    upstream_tasks = []


    def __lshift__(self, task2):
        """Implements Task << Task"""
        self.set_upstream(task2)

    def __rshift__(self, task2):
        """Implements Task >> Task"""
        self.set_downstream(task2)

    def set_upstream(self, tasks):

        if isinstance(tasks, Operator):
            tasks = [tasks]

        self.upstream_tasks = [task.task_id for task in tasks]

    def set_downstream(self, tasks):

        if isinstance(tasks, Operator):
            tasks = [tasks]

        self.downstream_tasks = [task.task_id for task in tasks]

        pass