from .. import fields, manager, model
from ..interaction import GenericInteraction


class TasksInteraction(GenericInteraction):
    path = "tasks"


class Task(model.Model):

    name = fields._Field("name")
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
    result = fields._Field("text", path=["result"])

    objects = manager.Manager(TasksInteraction())
