PROGIMAGE SERVER
-------------------

Provides a RESTful (JSON) API for image manipulation and a [client library](https://github.com/tobey/progimage-client)

Images serialized as base64 encoded strings:

```python
{
    'id': 'f909cd7e-6839-4b05-ae37-f52aa56091c7',
    'image': {'data': '/rwpinfmcdmwmq', 'type': 'image/jpeg'}
}
```


To Run locally, using docker
```python

docker-compose up

```
This will start a local mysql db and django app


Without docker
```
pip install -r requeirments.txt 

```

```
python manage.py migrate

```
```
python manage.py test

```

```
python manage.py runserver

```



API interface
--------------
Use [client library](https://github.com/tobey/progimage-client)



API methods (Fully documented using djangorestframework + coreapi)

```
GET /images/   
GET /images/<image_id>/  
GET /images/?id__in=<image_id>,<image_id>
GET /images/png/?id__in=<image_id>,<image_id>
GET /images/jpeg/?id__in=<image_id>,<image_id>
GET /images/giff/?id__in=<image_id>,<image_id>
GET /images/rotate/?id__in=<image_id>,<image_id>
GET /images/invert/?id__in=<image_id>,<image_id>
GET /images/url/?id__in=<image_id>,<image_id>
POST /images/ | multipart/form-data | image files
POST /images/ | application/json | image urls
```


NOTES
-----
* Restframework for api + Auth
* ThreadPoolExecutor for batch processing
* PIL for image processing