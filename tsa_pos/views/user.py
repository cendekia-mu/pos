from deform import widget
import colander
import deform

from ..models import User, UserGroup, Group, Permissions,UserPermission
from . import BaseViews
from ..i18n import _
from sqlalchemy.orm import Session


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

    perm_names = colander.SchemaNode(
        colander.Set(), 
        title=_("Permissions"),
        widget=widget.CheckboxChoiceWidget(values=[]),
    )

    def after_bind(self,  node, kw):
        # Populate group_id choices
        groups = Group.query().all()
        node['group_ids'].widget.values = [
            (str(group.id), group.description) for group in groups
        ]

        permission = Permissions.query().all()
        node['perm_names'].widget.values = [
            (p.name, p.description) for p in permission
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
    # BAGIAN GROUP (sudah benar)
        group_ids = set(values.get('group_ids', [])) #mengambil data group_id yang ada di form
        permissions = set(values.get('perm_names', [])) #mengambil data perm_name yang ada di form
        existing = set() #variabel yang berfungsi untuk menyiimpan data semnatara

        q = UserGroup.query().filter(UserGroup.user_id == row.id) #mengambil semua data yang dimiliki user di table usergroup
        y = UserPermission.query().filter(UserPermission.user_id == row.id) #mengambil semua data yang dimiliki dari user di table userpermission

        for up in y: #perulangan dulu karena akan dimasukan ke dalam variabel yang berupa array array 
            existing.add(str(up.perm_name)) #spesifik yang dimasukan itu hanya data perm_name saja

        for ug in q: #perulangan dulu karena akan dimasukan kedalam variabel yang berupa array
            existing.add(str(ug.group_id)) #spesifik yang dimasuukann itu hanya group_id saja

        # -------------------------
        # hapus GROUP
        # -------------------------
        delete_ids = existing - group_ids #data di variabel akan dikurangi oleh data yang sudah tidak ada di form
        for gid in delete_ids:

            # Aman konversi integer
            gid_str = str(gid).strip()
            try:
                gid_int = int(gid_str)
            except ValueError:
                # Jika bukan angka, skip saja
                continue

            q = UserGroup.query().filter(
                UserGroup.user_id == row.id,
                UserGroup.group_id == gid_int
            )
            ug = q.first()

            if ug:
                self.db_session.delete(ug)
                self.db_session.flush()

        # -------------------------
        # NEW GROUP
        # -------------------------
        new_ids = group_ids - existing
        for gid in new_ids:

            gid_str = str(gid).strip()
            try:
                gid_int = int(gid_str)
            except ValueError:
                # Jika input group_ids berisi teks tidak valid → skip
                continue

            new_ug = UserGroup(
                user_id=row.id,
                group_id=gid_int
            )
            self.db_session.add(new_ug)
            self.db_session.flush()

        # -------------------------
        # DELETE PERMISSIONS
        # -------------------------
        delete_ids = existing - permissions
        for perm_name in delete_ids:
            q = UserPermission.query().filter(
                UserPermission.user_id == row.id,
                UserPermission.perm_name == str(perm_name)
            )
            up = q.first()
            if up:
                self.db_session.delete(up)
                self.db_session.flush()

        # -------------------------
        # NEW PERMISSIONS
        # -------------------------
        new_ids = permissions - existing
        for perm_name in new_ids:
            new_up = UserPermission(
                user_id=row.id,
                perm_name=str(perm_name)
            )
            self.db_session.add(new_up)
            self.db_session.flush()

        return row



    def get_values(self, row):
        values = super().get_values(row)
        q = UserGroup.query().filter(UserGroup.user_id == row.id)
        group_ids = [str(ug.group_id) for ug in q]
        values['group_ids'] = set(group_ids)
        values['perm_names'] = {up.perm_name for up in row.user_permissions}
        return values
    
   
