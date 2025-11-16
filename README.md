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

Downgrade 
```
 $alembic -c config downgrade -1 or serial
```

InitializeDB 
```
$tsa-pos-db-init config
```
Starting 
```
$pserve config [--reload]
```