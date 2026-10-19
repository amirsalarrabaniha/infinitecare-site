from django.db import models


class ContactMessage(models.Model):
    LANGUAGES = [('en', 'English'), ('hu', 'Hungarian')]
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(max_length=5000)
    language = models.CharField(max_length=2, choices=LANGUAGES, default='en')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} <{self.email}>'
