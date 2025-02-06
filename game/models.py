from django.db import models
class ElemetsGame(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)
    button_text = models.CharField(max_length=255)
    true_rez = models.IntegerField(max_length=1)
    itog_txt = models.TextField(blank=True)

# dorm makemigrations
# dorm migrate