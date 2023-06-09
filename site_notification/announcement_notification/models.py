from django.db import models


class Newsletter(models.Model):
    email = models.EmailField()


    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"{self.email} - {self.date_created}"
