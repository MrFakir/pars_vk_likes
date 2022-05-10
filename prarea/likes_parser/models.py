from django.db import models


class GroupList(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название группы',
                             help_text='Введите название группы для отображения в списке')
    group_id = models.IntegerField(default=0, verbose_name='ID Группы')
    data = models.JSONField(null=False, default=dict, blank=True, verbose_name='Json данные')
    user_id = models.CharField(max_length=2, verbose_name='Тест поле для юзера', default=0, blank=True)

    def __str__(self):
        return str(self.group_id)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
