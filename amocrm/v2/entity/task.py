from .. import fields, manager, model
from ..filters import SingleFilter
from ..interaction import GenericInteraction
from ..register import get_model_by_name


class TasksInteraction(GenericInteraction):
    path = "tasks"


class Task(model.Model):
    entity_id = fields._Field("entity_id")
    entity_type = fields._Field("entity_type")

    name = fields._Field("name", blank=True)
    created_by = fields._Link("created_by", "User")
    updated_by = fields._Link("updated_by", "User")
    created_at = fields._DateTimeField("created_at")
    updated_at = fields._DateTimeField("updated_at")
    responsible_user = fields._Link("responsible_user_id", "User")
    is_completed = fields._Field("is_completed")
    task_type_id = fields._Field("task_type_id")
    text = fields._Field("text")
    duration_sec = fields._Field("duration")
    complete_till = fields._DateTimeField("complete_till")
    result = fields._Field("text", path=["result"], blank=True)

    objects = manager.Manager(TasksInteraction())

    @property
    def entity(self):
        models = {
            "leads": "Lead",
            "customers": "Customer",
            "contacts": "Contact",
            "companies": "Company",
        }
        if self.entity_type not in models:
            return None
        model = get_model_by_name(models.get(self.entity_type))
        return model.objects.get(object_id=self.entity_id)


class _TaskList:
    def __init__(self, entity_type, entity_id):
        self.entity_type = entity_type
        self.entity_id = entity_id

    def __iter__(self):
        return Task.objects.filter(
            filters=[SingleFilter("entity_type")(self.entity_type), SingleFilter("entity_id")(self.entity_id)]
        )

    def add(self, task: Task):
        task.entity_id = self.entity_id
        task.entity_type = self.entity_type
        task.save()


class TaskField(fields._BaseField):
    def __init__(self, entity_type):
        self._entity_type = entity_type
        super().__init__(blank=True)

    def on_get_instance(self, instance, values):
        return _TaskList(self._entity_type, instance.id)
