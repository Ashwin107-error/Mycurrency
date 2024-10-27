from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # e.g., USD, EUR
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, blank=True, null=True)

    def __str__(self):
        return self.code
    
class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey('Currency', related_name='source', on_delete=models.CASCADE)
    target_currency = models.ForeignKey('Currency', related_name='target', on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=20, decimal_places=6)
    date = models.DateField()
    fallback_details = models.JSONField(null=True, blank=True)  # Updated here

    def __str__(self):
        return f"{self.source_currency} to {self.target_currency} on {self.date}"
    
class CurrencyProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)  # E.g., "CurrencyBeacon", "MockProvider"
    priority = models.PositiveIntegerField()  # Lower numbers indicate higher priority

    def __str__(self):
        return self.name
