from django.db import models
from datetime import timedelta

class Client(models.Model):
    ROLE_CHOICES = [
        ('plaintiff', 'Истец (Клиент)'),
        ('defendant', 'Ответчик'),
        ('third_party', '3-я сторона'),
    ]
    name = models.CharField("ФИО / Название", max_length=255)
    role = models.CharField("Процессуальный статус", max_length=20, choices=ROLE_CHOICES, default='plaintiff')
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"

class Case(models.Model):
    STATUS_CHOICES = [('active', 'В производстве'), ('finished', 'Завершено')]
    title = models.CharField("Номер дела / Суд", max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases_as_plaintiff', verbose_name="Истец (Клиент)")
    defendant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='cases_as_defendant', verbose_name="Ответчик")
    start_date = models.DateField("Дата регистрации дела")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Дело {self.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # АВТОМАТИЗАЦИЯ: При создании дела создаем первое событие "Решение" на дату начала
            # Это в свою очередь запустит цепочку создания "Апелляции"
            CaseEvent.objects.create(
                case=self,
                event_type='decision',
                date_planned=self.start_date,
                comment="Автоматически создано при регистрации дела. Установите реальную дату решения."
            )

    class Meta:
        verbose_name = "Судебное дело"
        verbose_name_plural = "Судебные дела"

class CaseEvent(models.Model):
    EVENT_TYPES = [
        ('decision', 'Судебное решение'),
        ('appeal', 'Срок подачи апелляции'),
        ('execution', 'Исполнительное производство'),
    ]
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField("Этап", max_length=50, choices=EVENT_TYPES)
    date_planned = models.DateField("Срок выполнения")
    is_completed = models.BooleanField("Статус: Выполнено", default=False)
    comment = models.TextField("Заметки", blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # МАГИЯ ДАТ: Если создано "Решение", автоматически ставим "Апелляцию" на +30 дней
        if is_new and self.event_type == 'decision':
            CaseEvent.objects.create(
                case=self.case,
                event_type='appeal',
                date_planned=self.date_planned + timedelta(days=30),
                comment="Крайний срок обжалования (рассчитано автоматически: +30 дней)"
            )
        
        # Если апелляция отмечена как выполненная, создаем "Исполнительный лист" на +10 дней
        if not is_new and self.event_type == 'appeal' and self.is_completed:
            # Проверяем, нет ли уже такого события, чтобы не дублировать
            if not CaseEvent.objects.filter(case=self.case, event_type='execution').exists():
                CaseEvent.objects.create(
                    case=self.case,
                    event_type='execution',
                    date_planned=self.date_planned + timedelta(days=10),
                    comment="Срок получения исполнительного листа"
                )

    class Meta:
        verbose_name = "Событие дела"
        verbose_name_plural = "События дел"
        ordering = ['date_planned']