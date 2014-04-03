# -*- coding: utf-8 -*-
import os
from django.db import models
from myproj.settings import MEDIA_ROOT

def get_file_path(instance, filename):
    return os.path.join(str(instance.path),filename)

class Document(models.Model):    
    docfile = models.FileField(upload_to=get_file_path)
    
class Photo(models.Model):   
    file = models.FileField(upload_to=get_file_path)
    
    