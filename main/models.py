from django.db import models

# Create your models here.

class FileUpload(models.Model):
    title = models.TextField()
    cover = models.FileField(upload_to='/audio/')

    def __str__(self):
        return self.title
