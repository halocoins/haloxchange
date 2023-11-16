from django.db import models
from django.db.models import CharField, IntegerField, ImageField, ForeignKey
from django.db.models import DateTimeField, BooleanField
from datetime import datetime


class Token(models.Model):
    url_slug = CharField(max_length=20)
    address = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    symbol = CharField(max_length=10)
    decimals = CharField(max_length=20)
    listed_by = CharField(max_length=255)
    listed_on = DateTimeField(default=datetime.now)
    valid = BooleanField(default=True)
    icon_url = CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.url_slug


class TokenPolygon(models.Model):
    url_slug = CharField(max_length=20)
    address = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    symbol = CharField(max_length=10)
    decimals = CharField(max_length=20)
    listed_by = CharField(max_length=255)
    listed_on = DateTimeField(default=datetime.now)
    valid = BooleanField(default=True)
    icon_url = CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.url_slug


class TokenEthereum(models.Model):
    url_slug = CharField(max_length=20)
    address = CharField(max_length=50, unique=True)
    name = CharField(max_length=100)
    symbol = CharField(max_length=10)
    decimals = CharField(max_length=20)
    listed_by = CharField(max_length=255)
    listed_on = DateTimeField(default=datetime.now)
    valid = BooleanField(default=True)
    icon_url = CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.url_slug


class TokenData(models.Model):
    token = ForeignKey(Token, on_delete=models.CASCADE, unique=True)
    current_price = CharField(max_length=255)
    amount_to_sell = IntegerField()
    amount_to_buy = IntegerField()
    initial_sell_orders = BooleanField(default=False)
    initial_buy_orders = BooleanField(default=False)
    day_volume = CharField(max_length=255, default="0")
    day_volume_usd = CharField(max_length=255, default="0")
    market_make = BooleanField(default=False)
    market_make_volume = CharField(max_length=255, default="0")
    sell_fillers = CharField(max_length=10, default="10")
    buy_fillers = CharField(max_length=10, default="10")
    unreal_volume = CharField(max_length=255, default="0")
    unreal_volume_usd = CharField(max_length=255, default="0")

    def __str__(self):
        return str(self.token)


class TokenDataPolygon(models.Model):
    token = ForeignKey(TokenPolygon, on_delete=models.CASCADE, unique=True)
    current_price = CharField(max_length=255)
    amount_to_sell = IntegerField()
    amount_to_buy = IntegerField()
    initial_sell_orders = BooleanField(default=False)
    initial_buy_orders = BooleanField(default=False)
    day_volume = CharField(max_length=255, default="0")
    day_volume_usd = CharField(max_length=255, default="0")
    market_make = BooleanField(default=False)
    market_make_volume = CharField(max_length=255, default="0")
    sell_fillers = CharField(max_length=10, default="10")
    buy_fillers = CharField(max_length=10, default="10")
    unreal_volume = CharField(max_length=255, default="0")
    unreal_volume_usd = CharField(max_length=255, default="0")

    def __str__(self):
        return str(self.token)
    

class TokenDataEthereum(models.Model):
    token = ForeignKey(TokenEthereum, on_delete=models.CASCADE, unique=True)
    current_price = CharField(max_length=255)
    amount_to_sell = IntegerField()
    amount_to_buy = IntegerField()
    initial_sell_orders = BooleanField(default=False)
    initial_buy_orders = BooleanField(default=False)
    day_volume = CharField(max_length=255, default="0")
    day_volume_usd = CharField(max_length=255, default="0")
    market_make = BooleanField(default=False)
    market_make_volume = CharField(max_length=255, default="0")
    sell_fillers = CharField(max_length=10, default="10")
    buy_fillers = CharField(max_length=10, default="10")
    unreal_volume = CharField(max_length=255, default="0")
    unreal_volume_usd = CharField(max_length=255, default="0")

    def __str__(self):
        return str(self.token)


class ChartData(models.Model):
    token = ForeignKey(Token, on_delete=models.CASCADE)
    timestamp = DateTimeField(default=datetime.now)
    price = CharField(max_length=255)
    real = BooleanField(default=True)

    def __str__(self):
        return f'{self.token}->{self.price} - {self.timestamp}'


class ChartDataPolygon(models.Model):
    token = ForeignKey(TokenPolygon, on_delete=models.CASCADE)
    timestamp = DateTimeField(default=datetime.now)
    price = CharField(max_length=255)
    real = BooleanField(default=True)

    def __str__(self):
        return f'{self.token}->{self.price} - {self.timestamp}'



class ChartDataEthereum(models.Model):
    token = ForeignKey(TokenEthereum, on_delete=models.CASCADE)
    timestamp = DateTimeField(default=datetime.now)
    price = CharField(max_length=255)
    real = BooleanField(default=True)

    def __str__(self):
        return f'{self.token}->{self.price} - {self.timestamp}'



class BuyOrder(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(Token, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class BuyOrderPolygon(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(TokenPolygon, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class BuyOrderEthereum(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(TokenEthereum, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class SellOrder(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(Token, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class SellOrderPolygon(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(TokenPolygon, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class SellOrderEthereum(models.Model):
    order_id = CharField(max_length=50, unique=True)
    token = ForeignKey(TokenEthereum, on_delete=models.CASCADE)
    captured_price = CharField(max_length=50)
    price = CharField(max_length=255)
    amount = CharField(max_length=255)
    user = CharField(max_length=50)
    completed = CharField(max_length=255, null=True, blank=True)
    timestamp = DateTimeField(default=datetime.now)
    executed = BooleanField(default=False)
    can_revoke = BooleanField(default=False)  # False only for initial Orders
    real = BooleanField(default=True)
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.token}->{self.price}"


class OrderID(models.Model):
    order_id = CharField(max_length=50, unique=True)

    def __str__(self):
        return self.order_id


class OrderIDPolygon(models.Model):
    order_id = CharField(max_length=50, unique=True)

    def __str__(self):
        return self.order_id


class OrderIDEthereum(models.Model):
    order_id = CharField(max_length=50, unique=True)

    def __str__(self):
        return self.order_id


class TradeID(models.Model):
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.trade_id}"


class TradeIDPolygon(models.Model):
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.trade_id}"

class TradeIDEthereum(models.Model):
    trade_id = IntegerField(unique=True)

    def __str__(self):
        return f"{self.trade_id}"

