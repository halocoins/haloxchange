from django.contrib import admin
from .models import Token, TokenData, BuyOrder, SellOrder, OrderID, ChartData, TradeID
from .models import TokenPolygon, TokenDataPolygon, BuyOrderPolygon, SellOrderPolygon, OrderIDPolygon, ChartDataPolygon, TradeIDPolygon
from .models import TokenEthereum, TokenDataEthereum, BuyOrderEthereum, SellOrderEthereum, OrderIDEthereum, ChartDataEthereum, TradeIDEthereum

admin.site.register(Token)
admin.site.register(TokenData)
admin.site.register(BuyOrder)
admin.site.register(SellOrder)
admin.site.register(OrderID)
admin.site.register(ChartData)
admin.site.register(TradeID)

admin.site.register(TokenPolygon)
admin.site.register(TokenDataPolygon)
admin.site.register(BuyOrderPolygon)
admin.site.register(SellOrderPolygon)
admin.site.register(OrderIDPolygon)
admin.site.register(ChartDataPolygon)
admin.site.register(TradeIDPolygon)


admin.site.register(TokenEthereum)
admin.site.register(TokenDataEthereum)
admin.site.register(BuyOrderEthereum)
admin.site.register(SellOrderEthereum)
admin.site.register(OrderIDEthereum)
admin.site.register(ChartDataEthereum)
admin.site.register(TradeIDEthereum)

