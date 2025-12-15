## Login
### Screen
| Field     | Validation             |
| --------- | ---------------------- |
| User Name | not empty              |
| Password  | not empty              |
| Buttons   | Login, Reset, Register |

### Rule:
* UserName dan Password terdapat dalam tabel user

### Sukses
* Update Last Login Date
* Save Cookies

### Messages
* Login Berhasil
* Login Gagal

## Users
### Screen
| Field     | Validation                  |
| --------- | --------------------------- |
| User Name | Uniq                        |
| Email     | Uniq                        |
| Password  | Allow Empty                 |
| Confirm   | Allow Empty                 |
| Gropus    | List Groups dengan Checkbox |
| Buttons   | Save, Cancel                |

## Rule
* Jika Password diisi
  * bandingkan dengan confirm
  * save user dengan password
  
### Sukses
* Jika Baru
  * Set registered_date

### Messages
* Berhasil menambahkan User
* Gagal menambahkan User



