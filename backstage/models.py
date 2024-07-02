from django.db import models


class BackstageUserModel(models.Model):
    uid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=128)
    password = models.CharField(max_length=32)

    class Meta:
        db_table = 'backstage_user'

    def save(self, *args, **kwargs):
        import hashlib
        md5 = hashlib.md5()
        md5.update(self.password.encode())
        self.password = md5.hexdigest()
        super(BackstageUserModel, self).save(*args, **kwargs)


class ChannelModel(models.Model):
    cid = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=128)
    channel_code = models.CharField(max_length=64)
    credit_range = models.TextField(max_length=1024, null=True, blank=True)
    pay_url = models.TextField(max_length=1024, null=True, blank=True)
    qrcode = models.TextField(max_length=1024, null=True, blank=True)
    is_del = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'channel'


class OrderModel(models.Model):
    oid = models.AutoField(primary_key=True)
    order_no = models.CharField(max_length=32)

    # -1=> 处理中 1=>成功 2=>失败 5=>支付请求成功发送
    status = models.SmallIntegerField()

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    customer_id = models.PositiveIntegerField(null=True, blank=True)
    channel_id = models.PositiveIntegerField()
    tid = models.TextField(max_length=128, default=None)
    amount = models.IntegerField(null=True, blank=True)
    remark = models.TextField(max_length=2048, null=True, blank=True)

    class Meta:
        db_table = 'cashier_order'
