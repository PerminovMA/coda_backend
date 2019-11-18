from django.db import models


class Log(models.Model):
    WARNING_TYPE = 'WARNING'
    ERROR_TYPE = 'ERROR'
    INFO_TYPE = 'LOG'
    LOG_TYPE_CHOICES = [
        (ERROR_TYPE, 'Error'),
        (INFO_TYPE, 'Log'),
        (WARNING_TYPE, 'Warning'),
    ]

    log_type = models.CharField(max_length=6, choices=LOG_TYPE_CHOICES, default=ERROR_TYPE)
    function_name = models.CharField(max_length=200, blank=False, null=True)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class FBAccount(models.Model):
    GO_TYPE = 'GO'
    ACC_TYPES = [
        (GO_TYPE, 'GO'),
    ]

    amo_lead = models.ForeignKey('AmoLead', on_delete=models.CASCADE)
    acc_name = models.CharField(max_length=20, blank=False, null=False, unique=True)
    acc_type = models.CharField(max_length=20, choices=ACC_TYPES, default=GO_TYPE)
    add_date = models.DateTimeField(auto_now_add=True)

    def get_acc_index_number(self):
        return self.acc_name.replace(self.acc_type, '')

    def __str__(self):
        return self.acc_name


class AmoLead(models.Model):
    sold = models.BooleanField(default=False)  # Lead sale status
    amo_user = models.ForeignKey('AmoUser', on_delete=models.CASCADE)
    amo_lead_id = models.CharField(max_length=100, blank=False, null=False, unique=True)
    amo_status_id = models.CharField(max_length=100, blank=True, null=True)
    add_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.amo_lead_id


class AmoUser(models.Model):
    CC_TYPE = 'CC'  # credit card
    PAYOUT_TYPE_CHOICES = [
        (CC_TYPE, 'Credit card'),
    ]

    amo_user_id = models.CharField(max_length=100, blank=False, null=False, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True, default=None)
    responsible_user_id = models.CharField(max_length=255, blank=True, null=True, default=None)
    telegram_username = models.CharField(max_length=100, blank=True, null=True, default=None)
    chat_id = models.CharField(max_length=100, blank=True, null=True, default=None)
    ref_id = models.CharField(max_length=100, blank=True, null=True, default=None)
    amo_account_id = models.CharField(max_length=100, blank=True, null=True, default=None)
    facebook_link = models.URLField(blank=True, null=True, default=None)
    payout_method = models.CharField(max_length=20, default=CC_TYPE)
    cc_number = models.CharField(max_length=50, blank=True, null=True, default=None)
    fb_login = models.CharField(max_length=255, blank=True, null=True, default=None)
    fb_password = models.CharField(max_length=255, blank=True, null=True, default=None)
    acc_wall_raws = models.CharField(max_length=50, blank=True, null=True, default=None)
    acc_age = models.CharField(max_length=50, blank=True, null=True, default=None)
    acc_friends_quantity = models.CharField(max_length=50, blank=True, null=True, default=None)
    acc_chat_activity = models.CharField(max_length=50, blank=True, null=True, default=None)

    def __str__(self):
        return "{} id: {}".format(self.name, self.amo_user_id)
