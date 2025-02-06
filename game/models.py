from django.db import models
class ElemetsGame(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True)
    button_text = models.CharField(max_length=255)
    true_rez = models.IntegerField(max_length=1)
    itog_txt = models.TextField(blank=True)


class BotState(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    state = models.CharField(max_length=100, default='1')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user_id}: State {self.state}"

# dorm makemigrations
# dorm migrate