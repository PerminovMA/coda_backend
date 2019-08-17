from django.db import models


class Log(models.Model):
    ERROR_TYPE = 'ERROR'
    INFO_TYPE = 'LOG'
    LOG_TYPE_CHOICES = [
        (ERROR_TYPE, 'Error'),
        (INFO_TYPE, 'Log'),
    ]

    log_type = models.CharField(max_length=5, choices=LOG_TYPE_CHOICES, default=ERROR_TYPE)
    function_name = models.CharField(max_length=200, blank=False, null=True)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class AmoLead(models.Model):
    amo_user = models.ForeignKey('AmoUser', on_delete=models.CASCADE)
    amo_lead_id = models.CharField(max_length=100, blank=False, null=False)
    amo_account_id = models.CharField(max_length=100, blank=False, null=False)
    amo_status_id = models.CharField(max_length=100, blank=True, null=True)
    add_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['amo_lead_id', 'amo_account_id']]

    def __str__(self):
        return self.amo_lead_id


class AmoUser(models.Model):
    amo_user_id = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return self.amo_user_id
