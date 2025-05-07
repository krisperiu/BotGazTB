from django.db import models
from django.utils import timezone

class Report(models.Model):
    tg_id = models.BigIntegerField()
    name = models.CharField(max_length=20)
    text_rep = models.CharField(max_length=250)
    ranked = models.IntegerField()
    date = models.DateField()
    status = models.IntegerField()  
    comment_moder = models.CharField(max_length=250, blank=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def mark_as_reviewed(self, comment=""):
        self.comment_moder = comment
        self.status = 1
        self.reviewed_at = timezone.now()
        self.save()

    class Meta:
        managed = False  
        db_table = 'reports'

    def __str__(self):
        return f'Жалоба {self.id} от {self.name}'

class Photo(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='photos')
    photo_id = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'photos'