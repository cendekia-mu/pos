# Models Structure

## Users

Table Name: users

| Field Name         | Type         | Options        | Description |
| ------------------ | ------------ | -------------- | ----------- |
| id                 | Integer      | Auto Increment |             |
| user_name          | String       | Uniq           |             |
| user_password      | String       | sha256         |             |
| last_login_date    | DateTime     | timezone=False |             |
| status             | SmallInt     | User Status    | 0 disable   |
|                    |              |                | 1 enable    |
| email              | String(100)  | Uniq           |             |
| security_code      | Unicode(256) |                |             |
| registered_date    | DateTime     | timezone=False |             |
| security_code_date | DateTime     | timezone=False |             |

## Groups
Table Name: groups

| Field Name   | Type         | Options                   | Description |
| ------------ | ------------ | ------------------------- | ----------- |
| id           | Integer      | primary_key=True          | Auto Inc    |
| group_nameI  | Unicode(128) | unique=True               |             |
| description  | Text         |                           |             |
| member_count | Unicode(128) | unique=True               |             |
| group_nameI  | Integer      | nullable=False, default=0 |             |


    # lists app wide permissions we might want to assign to groups
    __possible_permissions__ = ()

    @declared_attr
    def (self):
        return sa.Column(sa.Text())

    @declared_attr
    def (self):
        return sa.Column(sa.Integer, nullable=False, default=0)

    @declared_attr
    def users(self):
        """ relationship for users belonging to this group"""
        return sa.orm.relationship(
            "User",
            secondary="users_groups",
            order_by="User.user_name",
            passive_deletes=True,
            passive_updates=True,
            backref="groups",
        )

    # dynamic property - useful
    @declared_attr
    def users_dynamic(self):
        """ dynamic relationship for users belonging to this group
            one can use filter """
        return sa.orm.relationship(
            "User", secondary="users_groups", order_by="User.user_name", lazy="dynamic", overlaps="groups,users"
        )

    @declared_attr
    def permissions(self):
        """ non-resource permissions assigned to this group"""
        return sa.orm.relationship(
            "GroupPermission",
            backref="groups",
            cascade="all, delete-orphan",
            passive_deletes=True,
            passive_updates=True,
        )

    @declared_attr
    def resource_permissions(self):
        """ permissions to specific resources this group has"""
        return sa.orm.relationship(
            "GroupResourcePermission",
            backref="groups",
            cascade="all, delete-orphan",
            passive_deletes=True,
            passive_updates=True,
        )

    @declared_attr
    def resources(self):
        """ Returns all resources directly owned by group, can be used to assign
        ownership of new resources::

            user.resources.append(resource) """
        return sa.orm.relationship(
            "Resource",
            cascade="all",
            passive_deletes=True,
            passive_updates=True,
            backref="owner_group",
        )

    @declared_attr
    def resources_dynamic(self):
        """ Returns all resources directly owned by group, can be used to assign
        ownership of new resources::

            user.resources.append(resource) """
        return sa.orm.relationship(
            "Resource",
            cascade="all",
            passive_deletes=True,
            passive_updates=True,
            lazy="dynamic",
            overlaps="owner_group,resources"
        )
## Permissions
## User Group
## User Permission
## Group Permisssion
## Product Category
## Provinsi
## Kabupaten/Kota
## Kecamatan
## Kelurahan
## Order
## Partner
## Invoice
## Chart Of Account
## Departemen
