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
