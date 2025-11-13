# pos


Install

```
$pip install -e .
```
Jika terjadi perubahan Model Jalankan perintah
```
 $alembic -c config revision --autogenerate -m "Keterangan"
```

Upgrade DB 
```
 $alembic -c config upgrade head
```

InitializeDB 
```
$tsa-pos-db-init config
```
Starting 
```
$pserve config [--reload]
```