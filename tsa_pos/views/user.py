from deform import widget
import colander
import deform

from ..models import User, UserGroup, Group
from . import BaseViews
from ..i18n import _


class ListSchema(colander.Schema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             title=_("Action"),
                             widget=widget.HiddenWidget())
    user_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    last_login_date = colander.SchemaNode(colander.DateTime(),
                                          missing=colander.drop)


class CreateSchema(colander.Schema):
    # Define your schema fields here
    user_name = colander.SchemaNode(colander.String())
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    user_password = colander.SchemaNode(colander.String(), widget=deform.widget.PasswordWidget(),
                                        missing=colander.drop,)
    group_ids = colander.SchemaNode(
        colander.Set(),
        widget=widget.CheckboxChoiceWidget(
            values=[],
        ),
    )

    def after_bind(self, schema, kw):
        # Populate group_id choices
        groups = Group.query().all()
        schema['group_ids'].widget.values = [
            (str(group.id), group.description) for group in groups
        ]


class UpdateSchema(CreateSchema):
    id = colander.SchemaNode(colander.Integer(),
                             missing=colander.drop,
                             widget=widget.HiddenWidget())


class Views(BaseViews):
    def __init__(self, request):
        super().__init__(request)
        self.table = User  # Assuming User is your SQLAlchemy model
        self.CreateSchema = CreateSchema
        self.UpdateSchema = UpdateSchema  # For simplicity, using the same schema
        self.ReadSchema = UpdateSchema  # For simplicity, using the same schema
        self.ListSchema = ListSchema
        self.list_route = 'user-list'

    def after_save(self, row, values):
        group_ids = set(values.get('group_ids', []))
        existing = set()
        q = UserGroup.query().filter(UserGroup.user_id == row.id)
        for ug in q:
            existing.add(str(ug.group_id))

        delete_ids = existing - group_ids
        for gid in delete_ids:
            q = UserGroup.query().filter(
                UserGroup.user_id == row.id,
                UserGroup.group_id == int(gid)
            )
            ug = q.first()
            if ug:
                self.db_session.delete(ug)
                self.db_session.flush()

        new_ids = group_ids - existing
        for gid in new_ids:
            new_ug = UserGroup(
                user_id=row.id,
                group_id=int(gid)
            )
            self.db_session.add(new_ug)
            self.db_session.flush()

        return row

    def get_values(self, row):
        values = super().get_values(row)
        q = UserGroup.query().filter(UserGroup.user_id == row.id)
        group_ids = [str(ug.group_id) for ug in q]
        values['group_ids'] = set(group_ids)
        return values
