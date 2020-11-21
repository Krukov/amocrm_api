from .. import fields, manager, model
from ..interaction import GenericInteraction


class StatusesInteraction(GenericInteraction):
    path = "leads/pipelines/{pipeline_id}/statuses"
    field = "statuses"

    def __init__(self, pipeline_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pipeline_id = pipeline_id

    def _get_path(self):
        return self.path.format(pipeline_id=self._pipeline_id)

    def get_all(self, include=None, query=None, filters=(), order=None):
        for data in self._all(self._get_path(), include=include, query=None, filters=filters, order=order):
            for status_data in data[self._get_field()]:
                if not query or status_data["name"].lower() == query.lower():
                    yield status_data


class Status(model.Model):
    name = fields._Field("name")
    sort = fields._Field("sort")
    is_editable = fields._Field("is_editable")
    color = fields._Field("color")
    type = fields._Field("type")

    @classmethod
    def get_for(cls, pipeline):
        if isinstance(pipeline, Pipeline):
            pipeline = pipeline.id
        return manager.Manager(interaction=StatusesInteraction(pipeline_id=pipeline), model=cls)


class _StatusField(fields._Field):
    _path = ["_embedded"]

    def __init__(self):
        super().__init__(name="statuses")

    def on_get(self, data):
        return [Status(data=item) for item in data]


class PipelinesInteraction(GenericInteraction):
    path = "leads/pipelines"
    field = "pipelines"


class Pipeline(model.Model):
    name = fields._Field("name")
    sort = fields._Field("sort")
    is_main = fields._Field("is_main")
    is_unsorted_on = fields._Field("is_unsorted_on")
    is_archive = fields._Field("is_archive")
    account_id = fields._Field("account_id")

    statuses = _StatusField()

    objects = manager.Manager(PipelinesInteraction())
