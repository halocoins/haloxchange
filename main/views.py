from operator import itemgetter
from itertools import groupby
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import requests
from .models import Token, TokenData, BuyOrder, SellOrder, OrderID, ChartData, TradeID
from .models import TokenPolygon, TokenDataPolygon, BuyOrderPolygon, SellOrderPolygon, OrderIDPolygon, ChartDataPolygon, TradeIDPolygon
from .models import TokenEthereum, TokenDataEthereum, BuyOrderEthereum, SellOrderEthereum, OrderIDEthereum, ChartDataEthereum, TradeIDEthereum
from datetime import datetime, timedelta
from django.utils import timezone
from django.core import serializers
import random
from django.db.models import IntegerField
from django.db.models.functions import Cast
from django.db.models import Max, Min, F, IntegerField
from django.db.models.functions import TruncDate


def fetch_currency_price(request, symbol):
    try:
        api_url = f"https://api.binance.us/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            bnb_price = data.get('price')
            return JsonResponse({'price': bnb_price})
        else:
            return JsonResponse({'error': 'Failed to fetch BNB Price'}, status=500)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f"An error occurred: {e}"}, status=500)


def index(request):
    tokens = Token.objects.all()
    first_token = []
    for token in tokens:
        first_token.append(token)
    if len(first_token) != 0:
        slug = first_token[0].url_slug
        address = first_token[0].address
        return redirect(f'/exchange/bsc/{address}/{slug}/')
    else:
        return HttpResponse("No token listed")


def exchange(request):
    all_tokens = Token.objects.all()
    data = {
        'tokens': all_tokens
    }
    return redirect('/')


def polygon_exchange(request):
    tokens = TokenPolygon.objects.all()
    first_token = []
    for token in tokens:
        first_token.append(token)
    if len(first_token) != 0:
        slug = first_token[0].url_slug
        address = first_token[0].address
        return redirect(f'/exchange/polygon/{address}/{slug}/')
    else:
        return HttpResponse("No token listed")


def ethereum_exchange(request):
    tokens = TokenEthereum.objects.all()
    first_token = []
    for token in tokens:
        first_token.append(token)
    if len(first_token) != 0:
        slug = first_token[0].url_slug
        address = first_token[0].address
        return redirect(f'/exchange/ethereum/{address}/{slug}/')
    else:
        return HttpResponse("No token listed")


# bsc-views---------


def tokens(request, symbol):
    all_tokens = TokenData.objects.all()
    if symbol != None and symbol != '':
        if (not Token.objects.filter(symbol=symbol).exists()):
            symbol = '_'
    else:
        symbol = '_'

    token_data = ""
    if symbol != '_':
        token = Token.objects.get(symbol=symbol)
        token_data = TokenData.objects.get(token=token)

    data = {
        'tokens': all_tokens,
        'token_data': token_data
    }
    return render(request, 'main/tokens.html', data)


def order_book(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        token = Token.objects.get(url_slug=url_slug_, address=address_)
        sellOrders = SellOrder.objects.filter(
            token=token, executed=False).order_by('-price')
        buyOrders = BuyOrder.objects.filter(
            token=token, executed=False).order_by('price')

        sell_orders = []
        for order in sellOrders:
            sell = [int(order.price) / 10**18, (int(order.amount) -
                                                int(order.completed)) / 10**int(token.decimals)]
            sell_orders.append(sell)

        buy_orders = []
        for order in buyOrders:
            buy = [int(order.price) / 10**18, (int(order.amount) -
                                               int(order.completed)) / 10**int(token.decimals)]
            buy_orders.append(buy)

        price = TokenData.objects.get(token=token).current_price
        return JsonResponse({'order_book': {'sell_orders': sell_orders, 'buy_orders': buy_orders, 'current_price': price}})


def recent_trades(request, address_):
    tokenInstance = Token.objects.get(address=address_)
    buyOrders = BuyOrder.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')
    sellOrders = SellOrder.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')

    sell_orders = []
    for order in sellOrders:
        sell = [int(order.price) / 10**18, int(order.completed) /
                10**int(tokenInstance.decimals)]
        sell_orders.append(sell)

    buy_orders = []
    for order in buyOrders:
        buy = [int(order.price) / 10**18, int(order.completed) /
               10**int(tokenInstance.decimals)]
        buy_orders.append(buy)

    return JsonResponse({'result': {'buy_trades': buy_orders, 'sell_trades': sell_orders}})


def order_history(request, address_, url_slug_, address):
    tokenInstance = Token.objects.get(url_slug=url_slug_, address=address_)
    token_buys = BuyOrder.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_sells = SellOrder.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_buys = serializers.serialize('json', token_buys)
    token_sells = serializers.serialize('json', token_sells)

    # ALL-PAIRS
    buy_orders = BuyOrder.objects.filter(user=address).order_by('-timestamp')
    sell_orders = SellOrder.objects.filter(user=address).order_by('-timestamp')
    all_buys = []
    all_sells = []
    for order in buy_orders:
        buy = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
               order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_buys.append(buy)

    for order in sell_orders:
        sell = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
                order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_sells.append(sell)

    return JsonResponse({'result': {'current_buy_orders': token_buys, 'current_sell_orders': token_sells, 'all_buys': all_buys, 'all_sells': all_sells}})


def home(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        all_tokens = Token.objects.filter(valid=True)
        all_tokens_data = TokenData.objects.all()
        token = Token.objects.get(url_slug=url_slug_, address=address_)
        tokenData = TokenData.objects.get(token=token)
        sellOrders = SellOrder.objects.filter(
            token=token, executed=False).order_by('price')
        buyOrders = BuyOrder.objects.filter(
            token=token, executed=False).order_by('-price')
        all_price = []
        for order in sellOrders:
            all_price.append(int(order.price))
        if (len(all_price) != 0):
            price = min(all_price)
        else:
            price = 0

        current_datetime = timezone.now()
        datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

        day_volume_ = 0
        day_volume_usd_ = 0
        day_high = 0
        day_low = 0

        new_tokens_all = Token.objects.filter(
            valid=True).order_by('-listed_on')
        new_tokens = []
        count = 0
        for token_ in new_tokens_all:
            if count < 10:
                new_tokens.append(token_)
                count += 1

        tokenData.day_volume = int(day_volume_)
        tokenData.day_volume_usd = int(day_volume_usd_)
        tokenData.save()

        day_volume_ += float(tokenData.unreal_volume)
        day_volume_usd_ += float(tokenData.unreal_volume_usd)
        print(day_volume_)

        trending_tokens = []
        all_token_data = TokenData.objects.all().annotate(day_volume_int=Cast(
            'day_volume', output_field=IntegerField())).order_by('day_volume_int')
        count = 0
        for token_ in all_token_data:
            if count < 10:
                trending_tokens.append(token_.token)
                count += 1

        mode = request.GET.get('mode')

        data = {
            "allTokens": all_tokens_data,
            "token": token,
            "tokenData": tokenData,
            "sellOrders": sellOrders,
            "buyOrders": buyOrders,
            "current_price": price,
            "day_volume": day_volume_,
            "day_volume_usd": day_volume_usd_,
            "day_high": day_high,
            "day_low": day_low,
            "url_slug": url_slug_,
            "new_tokens": new_tokens,
            "trending_tokens": trending_tokens,
            "chain": 'bsc',
            "currency": 'BNB',
            "default_icon": '/static/main/images/token.png',
            "explorer": 'https://bscscan.com',
            "mode": mode
        }

        if (not token.valid):
            return redirect('/')

        return render(request, 'main/home.html', data)


def day_volumes(request, address):
    token = Token.objects.get(address=address)
    tokenData = TokenData.objects.get(token=token)
    price = tokenData.current_price
    current_datetime = timezone.now()
    datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)
    sellOrders = SellOrder.objects.filter(
        token=token, executed=False).order_by('price')
    buyOrders = BuyOrder.objects.filter(
        token=token, executed=False).order_by('-price')

    day_volume_ = 0
    day_volume_usd_ = 0
    day_high = 0
    day_low = 0
    day_sell_orders = SellOrder.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    day_buy_orders = BuyOrder.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    for order in day_sell_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)
    for order in day_buy_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)

    if (len(day_sell_orders) > 0):
        day_high = int(day_sell_orders[0].price)
        day_low = int(day_sell_orders[0].price)
        for order in day_sell_orders:
            if int(order.price) > day_high:
                day_high = int(order.price)
            if int(order.price) < day_low:
                day_low = int(order.price)
    else:
        day_high = price
        day_low = price

    if float(day_volume_) > float(tokenData.day_volume):
        tokenData.day_volume = day_volume_
    if float(day_volume_usd_) > float(tokenData.day_volume_usd):
        tokenData.day_volume_usd = day_volume_usd_

    day_volume_ = tokenData.day_volume
    day_volume_usd_ = tokenData.day_volume_usd
    tokenData.save()
    if (tokenData.market_make):
        day_volume_ = float(tokenData.unreal_volume) + \
            float(tokenData.day_volume)
        day_volume_usd_ = float(tokenData.unreal_volume_usd) + \
            float(tokenData.day_volume_usd)

    # collecting burn amount
    completed_orders = 0
    for order in buyOrders:
        completed_orders += int(order.completed)
    for order in sellOrders:
        completed_orders += int(order.completed)

    burned = completed_orders / 10 ** int(token.decimals)
    burned = (0.07 / 100) * burned

    return JsonResponse({'day_data': {'volume': day_volume_, 'volume_usd': day_volume_usd_, 'day_high': day_high, 'day_low': day_low, 'burned': burned}})


def list_token(request):
    if request.method == 'POST':

        address = request.POST.get('address')
        name = request.POST.get('name')
        symbol = request.POST.get('symbol')
        decimals = request.POST.get('decimals')
        user = request.POST.get('user')
        icon_url = request.POST.get('icon_url')
        symbol_ = ''
        valid = "abcdefghijklmnopqrstuvwxyz0123456789"
        for char in symbol:
            if char.lower() not in valid:
                symbol_ += "_"
            else:
                symbol_ += char
        symbol = symbol
        url_slug = symbol + '_USD'

        new_token = Token(url_slug=url_slug, address=address, name=name,
                          symbol=symbol, decimals=decimals, listed_by=user, icon_url=icon_url)
        new_token.save()

        token = Token.objects.get(url_slug=url_slug)
        new_data = TokenData(token=token, current_price=0,
                             amount_to_sell=0, amount_to_buy=0)
        new_data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_market_sell(request, token):
    sellOrders = SellOrder.objects.filter(
        token=token, executed=False).order_by('price')

    id_list = []
    if (len(sellOrders) != 0):
        price = int(sellOrders[0].price)
        for order in sellOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def get_market_buy(request, token):
    tokenInstance = Token.objects.get(address=token)
    buyOrders = BuyOrder.objects.filter(
        token=tokenInstance, executed=False).order_by('price')

    id_list = []
    if (len(buyOrders) != 0):
        price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def get_max_buy_price(request, token):
    tokenInstance = Token.objects.get(address=token)
    buyOrders = BuyOrder.objects.filter(
        token=tokenInstance, executed=False).order_by('price')
    if (len(buyOrders) != 0):
        max_price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) > max_price:
                max_price = int(order.price)
    else:
        max_price = -1
    return JsonResponse({'max_price': max_price})


def check_sell_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = Token.objects.get(address=address_)
        orders = SellOrder.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) <= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def check_buy_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = Token.objects.get(address=address_)
        orders = BuyOrder.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) >= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def place_buy_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = Token.objects.get(address=token)

        found_orders = SellOrder.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) <= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True
        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_buy = int(amount)
            for id_ in orders:
                order = SellOrder.objects.get(order_id=id_)
                if int(order.price) <= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_buy > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_buy >= amount_check:
                        amount_to_buy -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_buy < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_buy)
                        amount_to_buy = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_buy <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_buy_order = BuyOrder(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                 price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_buy_order.save()

        # checking for any price updates
        token_data = TokenData.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartData(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrder.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            else:
                all_price = []
                buyOrders = BuyOrder.objects.filter(
                    token=tokenInstance, executed=False)
                for order in buyOrders:
                    all_price.append(int(order.price))
                if (len(all_price) != 0):
                    price_ = max(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartData(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def place_sell_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = Token.objects.get(address=token)

        found_orders = BuyOrder.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) >= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True

        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_sell = int(amount)
            for id_ in orders:
                order = BuyOrder.objects.get(order_id=id_)
                print(order.price, "---------")
                print(price, "---------")
                if int(order.price) >= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_sell > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_sell >= amount_check:
                        amount_to_sell -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_sell < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_sell)
                        amount_to_sell = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_sell <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_sell_order = SellOrder(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                   price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_sell_order.save()

        # checking for any price updates
        token_data = TokenData.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartData(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrder.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartData(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def revoke_buy_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (BuyOrder.objects.filter(order_id=order_id).exists()):
            order = BuyOrder.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def revoke_sell_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (SellOrder.objects.filter(order_id=order_id).exists()):
            order = SellOrder.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def new_order_id(request):
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderID.objects.filter(order_id=bit).exists()):
            new_id = OrderID(order_id=bit)
            new_id.save()
            exist = False
            return JsonResponse({'new_id': bit})


def new_order_id_internal():
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderID.objects.filter(order_id=bit).exists()):
            new_id = OrderID(order_id=bit)
            new_id.save()
            exist = False
            return bit


def play_chart(request):
    return render(request, 'main/chart.html')


def chart(request, address_):
    # Query to group data by date and calculate OHLC values
    token_instance = Token.objects.get(address=address_)
    available_dates = ChartData.objects.filter(token=token_instance).values_list(
        'timestamp__date', flat=True).distinct()

    chart_data = []
    for entry_date in available_dates:
        data_for_day = ChartData.objects.filter(
            token=token_instance, timestamp__date=entry_date)
        high = data_for_day.aggregate(Max('price'))['price__max']
        low = data_for_day.aggregate(Min('price'))['price__min']
        open_price = data_for_day.earliest('timestamp').price
        close_price = data_for_day.latest('timestamp').price

        chart_data.append({
            'time': entry_date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
        })

    return JsonResponse(chart_data, safe=False)


def control(request):
    return render(request, 'main/control.html')


def number_of_listed_tokens(request, address_):
    listed_tokens = Token.objects.filter(listed_by=address_)
    number = len(listed_tokens)
    return JsonResponse({'listed': number})


def all_listed_tokens(request):
    all_tokens = Token.objects.filter(valid=True)
    all_tokens = serializers.serialize("json", all_tokens)
    return JsonResponse({'all_tokens': all_tokens})


def market_maker(request):
    if request.method == 'POST':
        token_address = request.POST.get('market-make-address')
        volume = request.POST.get('market-make-volume')
        user_address = request.POST.get('user-address')
        market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'
        if user_address != market_maker:
            return JsonResponse({'success': False, 'error': 'Invalid Market Maker Address'})

        volume = int(volume)
        token = Token.objects.get(address=token_address)
        decimals = token.decimals
        actual_volume = volume * 10 ** int(decimals)
        print(actual_volume)
        per_order_amount_max = int(actual_volume / 30)
        percent_deviation = (10 * per_order_amount_max) / 100
        per_order_amount_min = int(per_order_amount_max - percent_deviation)
        current_price = TokenData.objects.get(token=token).current_price
        current_price = int(current_price)
        price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
        price_deivation = int(price_deivation)

        running_price_sell = current_price + price_deivation
        running_price_buy = current_price - price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_sell_order = SellOrder(order_id=order_id, token=token, captured_price=0,
                                       price=running_price_sell, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_sell_order.save()
            new_chart_data = ChartData(
                token=token, price=int(running_price_sell)/10**18)
            new_chart_data.save()
            running_price_sell = running_price_sell + price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_buy_order = BuyOrder(order_id=order_id, token=token, captured_price=0,
                                     price=running_price_buy, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_buy_order.save()
            new_chart_data = ChartData(
                token=token, price=int(running_price_buy)/10**18)
            new_chart_data.save()
            running_price_buy = running_price_buy - price_deivation

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def auto_market_maker(request, token):
    token_instance = Token.objects.get(address=token)
    token_data = TokenData.objects.get(token=token_instance)
    market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'

    if not token_data.market_make:
        return JsonResponse({'success': False, 'error': 'Market Maker is not enabled for this Token'})

    volume = int(token_data.market_make_volume) * \
        10 ** int(token_instance.decimals)
    sell_fillers = int(token_data.sell_fillers)
    buy_fillers = int(token_data.buy_fillers)
    current_price = int(token_data.current_price)

    per_order_amount = int(volume / 30)
    percent_deviation = (20 * per_order_amount) / 100
    per_order_amount_max = int(per_order_amount + percent_deviation)
    per_order_amount_min = int(per_order_amount - percent_deviation)

    price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
    price_deivation = int(price_deivation)

    running_price_sell = current_price + price_deivation
    running_price_buy = current_price - price_deivation

    sell_prices = []
    buy_prices = []

    for _ in range(sell_fillers):
        sell_prices.append(running_price_sell)
        running_price_sell += price_deivation

    for _ in range(buy_fillers):
        buy_prices.append(running_price_buy)
        running_price_buy -= price_deivation

    buy_filled_already = len(BuyOrder.objects.filter(
        token=token_instance, executed=False, real=False))
    sell_filled_already = len(SellOrder.objects.filter(
        token=token_instance, executed=False, real=False))

    if buy_filled_already < buy_fillers:
        print(1)
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(buy_prices)
        new_buy_order = BuyOrder(order_id=order_id, token=token_instance, captured_price=0,
                                 price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_buy_order.save()
        new_chart_data = ChartData(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()

        token_data.unreal_volume = float(
            token_data.unreal_volume) + float(amount)
        token_data.unreal_volume_usd = float(token_data.unreal_volume_usd) + (
            (float(amount) / 10 ** int(token_instance.decimals)) * float(price))
        token_data.save()

    else:
        print(2)
        buy_executed_already = len(BuyOrder.objects.filter(
            token=token_instance, executed=True, real=False))

        if buy_executed_already < 15:
            print(3)
            first_order = BuyOrder.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            print(4)
            first_executed_order = BuyOrder.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    if sell_filled_already < sell_fillers:
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(sell_prices)
        new_sell_order = SellOrder(order_id=order_id, token=token_instance, captured_price=0,
                                   price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_sell_order.save()
        new_chart_data = ChartData(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()
    else:
        sell_executed_already = len(SellOrder.objects.filter(
            token=token_instance, executed=True, real=False))

        if sell_executed_already < 15:
            first_order = SellOrder.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            first_executed_order = SellOrder.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    return JsonResponse({'success': True})


def generate_unique_trade_id():
    all_trade_ids = TradeID.objects.all()

    id_ = None
    if len(all_trade_ids) == 0:
        id_ = 1
    else:
        last_id = TradeID.objects.last()
        id_ = last_id.trade_id
        id_ += 1

    new_id = TradeID(trade_id=id_)
    new_id.save()

    return id_


# polygon-views---------

def polygon_tokens(request, symbol):
    all_tokens = TokenDataPolygon.objects.all()
    if symbol != None and symbol != '':
        if (not TokenPolygon.objects.filter(symbol=symbol).exists()):
            symbol = '_'
    else:
        symbol = '_'

    token_data = ""
    if symbol != '_':
        token = TokenPolygon.objects.get(symbol=symbol)
        token_data = TokenDataPolygon.objects.get(token=token)

    data = {
        'tokens': all_tokens,
        'token_data': token_data
    }
    return render(request, 'main/tokens.html', data)


def polygon_order_book(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        token = TokenPolygon.objects.get(url_slug=url_slug_, address=address_)
        sellOrders = SellOrderPolygon.objects.filter(
            token=token, executed=False).order_by('-price')
        buyOrders = BuyOrderPolygon.objects.filter(
            token=token, executed=False).order_by('price')

        sell_orders = []
        for order in sellOrders:
            sell = [int(order.price) / 10**18, (int(order.amount) -
                                                int(order.completed)) / 10**int(token.decimals)]
            sell_orders.append(sell)

        buy_orders = []
        for order in buyOrders:
            buy = [int(order.price) / 10**18, (int(order.amount) -
                                               int(order.completed)) / 10**int(token.decimals)]
            buy_orders.append(buy)

        price = TokenDataPolygon.objects.get(token=token).current_price
        return JsonResponse({'order_book': {'sell_orders': sell_orders, 'buy_orders': buy_orders, 'current_price': price}})


def polygon_recent_trades(request, address_):
    tokenInstance = TokenPolygon.objects.get(address=address_)
    buyOrders = BuyOrderPolygon.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')
    sellOrders = SellOrderPolygon.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')

    sell_orders = []
    for order in sellOrders:
        sell = [int(order.price) / 10**18, int(order.completed) /
                10**int(tokenInstance.decimals)]
        sell_orders.append(sell)

    buy_orders = []
    for order in buyOrders:
        buy = [int(order.price) / 10**18, int(order.completed) /
               10**int(tokenInstance.decimals)]
        buy_orders.append(buy)

    return JsonResponse({'result': {'buy_trades': buy_orders, 'sell_trades': sell_orders}})


def polygon_order_history(request, address_, url_slug_, address):
    tokenInstance = TokenPolygon.objects.get(
        url_slug=url_slug_, address=address_)
    token_buys = BuyOrderPolygon.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_sells = SellOrderPolygon.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_buys = serializers.serialize('json', token_buys)
    token_sells = serializers.serialize('json', token_sells)

    # ALL-PAIRS
    buy_orders = BuyOrderPolygon.objects.filter(
        user=address).order_by('-timestamp')
    sell_orders = SellOrderPolygon.objects.filter(
        user=address).order_by('-timestamp')
    all_buys = []
    all_sells = []
    for order in buy_orders:
        buy = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
               order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_buys.append(buy)

    for order in sell_orders:
        sell = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
                order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_sells.append(sell)

    return JsonResponse({'result': {'current_buy_orders': token_buys, 'current_sell_orders': token_sells, 'all_buys': all_buys, 'all_sells': all_sells}})


def polygon_home(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        all_tokens = TokenPolygon.objects.filter(valid=True)
        all_tokens_data = TokenDataPolygon.objects.all()
        token = TokenPolygon.objects.get(url_slug=url_slug_, address=address_)
        tokenData = TokenDataPolygon.objects.get(token=token)
        sellOrders = SellOrderPolygon.objects.filter(
            token=token, executed=False).order_by('price')
        buyOrders = BuyOrderPolygon.objects.filter(
            token=token, executed=False).order_by('-price')
        all_price = []
        for order in sellOrders:
            all_price.append(int(order.price))
        if (len(all_price) != 0):
            price = min(all_price)
        else:
            price = 0

        current_datetime = timezone.now()
        datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

        day_volume_ = 0
        day_volume_usd_ = 0
        day_high = 0
        day_low = 0

        new_tokens_all = TokenPolygon.objects.filter(
            valid=True).order_by('-listed_on')
        new_tokens = []
        count = 0
        for token_ in new_tokens_all:
            if count < 10:
                new_tokens.append(token_)
                count += 1

        tokenData.day_volume = int(day_volume_)
        tokenData.day_volume_usd = int(day_volume_usd_)
        tokenData.save()

        day_volume_ += float(tokenData.unreal_volume)
        day_volume_usd_ += float(tokenData.unreal_volume_usd)
        print(day_volume_)

        trending_tokens = []
        all_token_data = TokenDataPolygon.objects.all().annotate(day_volume_int=Cast(
            'day_volume', output_field=IntegerField())).order_by('day_volume_int')
        count = 0
        for token_ in all_token_data:
            if count < 10:
                trending_tokens.append(token_.token)
                count += 1
        mode = request.GET.get('mode')

        data = {
            "allTokens": all_tokens_data,
            "token": token,
            "tokenData": tokenData,
            "sellOrders": sellOrders,
            "buyOrders": buyOrders,
            "current_price": price,
            "day_volume": day_volume_,
            "day_volume_usd": day_volume_usd_,
            "day_high": day_high,
            "day_low": day_low,
            "url_slug": url_slug_,
            "new_tokens": new_tokens,
            "trending_tokens": trending_tokens,
            "chain": 'polygon',
            "currency": 'MATIC',
            "default_icon": '/static/main/images/polygon.png',
            "explorer": 'https://polygonscan.com',
            "mode": mode
        }

        if (not token.valid):
            return redirect('/')

        return render(request, 'main/home.html', data)


def polygon_day_volumes(request, address):
    token = TokenPolygon.objects.get(address=address)
    tokenData = TokenDataPolygon.objects.get(token=token)
    sellOrders = SellOrderPolygon.objects.filter(
        token=token, executed=False).order_by('price')
    buyOrders = BuyOrderPolygon.objects.filter(
        token=token, executed=False).order_by('-price')
    price = tokenData.current_price
    current_datetime = timezone.now()
    datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

    day_volume_ = 0
    day_volume_usd_ = 0
    day_high = 0
    day_low = 0
    day_sell_orders = SellOrderPolygon.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    day_buy_orders = BuyOrderPolygon.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    for order in day_sell_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)
    for order in day_buy_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)

    if (len(day_sell_orders) > 0):
        day_high = int(day_sell_orders[0].price)
        day_low = int(day_sell_orders[0].price)
        for order in day_sell_orders:
            if int(order.price) > day_high:
                day_high = int(order.price)
            if int(order.price) < day_low:
                day_low = int(order.price)
    else:
        day_high = price
        day_low = price

    if float(day_volume_) > float(tokenData.day_volume):
        tokenData.day_volume = day_volume_
    if float(day_volume_usd_) > float(tokenData.day_volume_usd):
        tokenData.day_volume_usd = day_volume_usd_

    day_volume_ = tokenData.day_volume
    day_volume_usd_ = tokenData.day_volume_usd
    tokenData.save()
    if (tokenData.market_make):
        day_volume_ = float(tokenData.unreal_volume) + \
            float(tokenData.day_volume)
        day_volume_usd_ = float(tokenData.unreal_volume_usd) + \
            float(tokenData.day_volume_usd)

    # collecting burn amount

    completed_orders = 0
    for order in buyOrders:
        completed_orders += int(order.completed)
    for order in sellOrders:
        completed_orders += int(order.completed)

    burned = completed_orders / 10 ** int(token.decimals)
    burned = (0.07 / 100) * burned

    return JsonResponse({'day_data': {'volume': day_volume_, 'volume_usd': day_volume_usd_, 'day_high': day_high, 'day_low': day_low, 'burned': burned}})


def polygon_list_token(request):
    if request.method == 'POST':

        address = request.POST.get('address')
        name = request.POST.get('name')
        symbol = request.POST.get('symbol')
        decimals = request.POST.get('decimals')
        user = request.POST.get('user')
        icon_url = request.POST.get('icon_url')
        symbol_ = ''
        valid = "abcdefghijklmnopqrstuvwxyz0123456789"
        for char in symbol:
            if char.lower() not in valid:
                symbol_ += "_"
            else:
                symbol_ += char
        symbol = symbol
        url_slug = symbol + '_USD'

        new_token = TokenPolygon(url_slug=url_slug, address=address, name=name,
                                 symbol=symbol, decimals=decimals, listed_by=user, icon_url=icon_url)
        new_token.save()

        token = TokenPolygon.objects.get(url_slug=url_slug)
        new_data = TokenDataPolygon(token=token, current_price=0,
                                    amount_to_sell=0, amount_to_buy=0)
        new_data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_get_market_sell(request, token):
    sellOrders = SellOrderPolygon.objects.filter(
        token=token, executed=False).order_by('price')

    id_list = []
    if (len(sellOrders) != 0):
        price = int(sellOrders[0].price)
        for order in sellOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def polygon_get_market_buy(request, token):
    tokenInstance = TokenPolygon.objects.get(address=token)
    buyOrders = BuyOrderPolygon.objects.filter(
        token=tokenInstance, executed=False).order_by('price')

    id_list = []
    if (len(buyOrders) != 0):
        price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def polygon_get_max_buy_price(request, token):
    tokenInstance = TokenPolygon.objects.get(address=token)
    buyOrders = BuyOrderPolygon.objects.filter(
        token=tokenInstance, executed=False).order_by('price')
    if (len(buyOrders) != 0):
        max_price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) > max_price:
                max_price = int(order.price)
    else:
        max_price = -1
    return JsonResponse({'max_price': max_price})


def polygon_check_sell_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = TokenPolygon.objects.get(address=address_)
        orders = SellOrderPolygon.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) <= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_check_buy_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = TokenPolygon.objects.get(address=address_)
        orders = BuyOrderPolygon.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) >= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_place_buy_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = TokenPolygon.objects.get(address=token)

        found_orders = SellOrderPolygon.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) <= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True
        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_buy = int(amount)
            for id_ in orders:
                order = SellOrderPolygon.objects.get(order_id=id_)
                if int(order.price) <= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_buy > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_buy >= amount_check:
                        amount_to_buy -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_buy < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_buy)
                        amount_to_buy = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_buy <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_buy_order = BuyOrderPolygon(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                        price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_buy_order.save()

        # checking for any price updates
        token_data = TokenDataPolygon.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartDataPolygon(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrderPolygon.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            else:
                all_price = []
                buyOrders = BuyOrderPolygon.objects.filter(
                    token=tokenInstance, executed=False)
                for order in buyOrders:
                    all_price.append(int(order.price))
                if (len(all_price) != 0):
                    price_ = max(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartDataPolygon(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_place_sell_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = TokenPolygon.objects.get(address=token)

        found_orders = BuyOrderPolygon.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) >= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True

        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_sell = int(amount)
            for id_ in orders:
                order = BuyOrderPolygon.objects.get(order_id=id_)
                print(order.price, "---------")
                print(price, "---------")
                if int(order.price) >= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_sell > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_sell >= amount_check:
                        amount_to_sell -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_sell < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_sell)
                        amount_to_sell = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_sell <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_sell_order = SellOrderPolygon(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                          price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_sell_order.save()

        # checking for any price updates
        token_data = TokenDataPolygon.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartDataPolygon(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrderPolygon.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartDataPolygon(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_revoke_buy_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (BuyOrderPolygon.objects.filter(order_id=order_id).exists()):
            order = BuyOrderPolygon.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def polygon_revoke_sell_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (SellOrderPolygon.objects.filter(order_id=order_id).exists()):
            order = SellOrderPolygon.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def polygon_new_order_id(request):
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderIDPolygon.objects.filter(order_id=bit).exists()):
            new_id = OrderIDPolygon(order_id=bit)
            new_id.save()
            exist = False
            return JsonResponse({'new_id': bit})


def polygon_new_order_id_internal():
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderIDPolygon.objects.filter(order_id=bit).exists()):
            new_id = OrderIDPolygon(order_id=bit)
            new_id.save()
            exist = False
            return bit


def polygon_play_chart(request):
    return render(request, 'main/chart.html')


def polygon_chart(request, address_):
    # Query to group data by date and calculate OHLC values
    token_instance = TokenPolygon.objects.get(address=address_)
    available_dates = ChartDataPolygon.objects.filter(token=token_instance).values_list(
        'timestamp__date', flat=True).distinct()

    chart_data = []
    for entry_date in available_dates:
        data_for_day = ChartDataPolygon.objects.filter(
            token=token_instance, timestamp__date=entry_date)
        high = data_for_day.aggregate(Max('price'))['price__max']
        low = data_for_day.aggregate(Min('price'))['price__min']
        open_price = data_for_day.earliest('timestamp').price
        close_price = data_for_day.latest('timestamp').price

        chart_data.append({
            'time': entry_date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close_price,
        })

    return JsonResponse(chart_data, safe=False)


def polygon_control(request):
    return render(request, 'main/control.html')


def polygon_number_of_listed_tokens(request, address_):
    listed_tokens = TokenPolygon.objects.filter(listed_by=address_)
    number = len(listed_tokens)
    return JsonResponse({'listed': number})


def polygon_all_listed_tokens(request):
    all_tokens = TokenPolygon.objects.filter(valid=True)
    all_tokens = serializers.serialize("json", all_tokens)
    return JsonResponse({'all_tokens': all_tokens})


def polygon_market_maker(request):
    if request.method == 'POST':
        token_address = request.POST.get('market-make-address')
        volume = request.POST.get('market-make-volume')
        user_address = request.POST.get('user-address')
        market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'
        if user_address != market_maker:
            return JsonResponse({'success': False, 'error': 'Invalid Market Maker Address'})

        volume = int(volume)
        token = TokenPolygon.objects.get(address=token_address)
        decimals = token.decimals
        actual_volume = volume * 10 ** int(decimals)
        print(actual_volume)
        per_order_amount_max = int(actual_volume / 30)
        percent_deviation = (10 * per_order_amount_max) / 100
        per_order_amount_min = int(per_order_amount_max - percent_deviation)
        current_price = TokenDataPolygon.objects.get(token=token).current_price
        current_price = int(current_price)
        price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
        price_deivation = int(price_deivation)

        running_price_sell = current_price + price_deivation
        running_price_buy = current_price - price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_sell_order = SellOrderPolygon(order_id=order_id, token=token, captured_price=0,
                                              price=running_price_sell, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_sell_order.save()
            new_chart_data = ChartDataPolygon(
                token=token, price=int(running_price_sell)/10**18)
            new_chart_data.save()
            running_price_sell = running_price_sell + price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_buy_order = BuyOrderPolygon(order_id=order_id, token=token, captured_price=0,
                                            price=running_price_buy, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_buy_order.save()
            new_chart_data = ChartDataPolygon(
                token=token, price=int(running_price_buy)/10**18)
            new_chart_data.save()
            running_price_buy = running_price_buy - price_deivation

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def polygon_auto_market_maker(request, token):
    token_instance = TokenPolygon.objects.get(address=token)
    token_data = TokenDataPolygon.objects.get(token=token_instance)
    market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'

    if not token_data.market_make:
        return JsonResponse({'success': False, 'error': 'Market Maker is not enabled for this Token'})

    volume = int(token_data.market_make_volume) * \
        10 ** int(token_instance.decimals)
    sell_fillers = int(token_data.sell_fillers)
    buy_fillers = int(token_data.buy_fillers)
    current_price = int(token_data.current_price)

    per_order_amount = int(volume / 30)
    percent_deviation = (20 * per_order_amount) / 100
    per_order_amount_max = int(per_order_amount + percent_deviation)
    per_order_amount_min = int(per_order_amount - percent_deviation)

    price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
    price_deivation = int(price_deivation)

    running_price_sell = current_price + price_deivation
    running_price_buy = current_price - price_deivation

    sell_prices = []
    buy_prices = []

    for _ in range(sell_fillers):
        sell_prices.append(running_price_sell)
        running_price_sell += price_deivation

    for _ in range(buy_fillers):
        buy_prices.append(running_price_buy)
        running_price_buy -= price_deivation

    buy_filled_already = len(BuyOrderPolygon.objects.filter(
        token=token_instance, executed=False, real=False))
    sell_filled_already = len(SellOrderPolygon.objects.filter(
        token=token_instance, executed=False, real=False))

    if buy_filled_already < buy_fillers:
        print(1)
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(buy_prices)
        new_buy_order = BuyOrderPolygon(order_id=order_id, token=token_instance, captured_price=0,
                                        price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_buy_order.save()
        new_chart_data = ChartDataPolygon(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()

        token_data.unreal_volume = float(
            token_data.unreal_volume) + float(amount)
        token_data.unreal_volume_usd = float(token_data.unreal_volume_usd) + (
            (float(amount) / 10 ** int(token_instance.decimals)) * float(price))
        token_data.save()

    else:
        print(2)
        buy_executed_already = len(BuyOrderPolygon.objects.filter(
            token=token_instance, executed=True, real=False))

        if buy_executed_already < 15:
            print(3)
            first_order = BuyOrderPolygon.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            print(4)
            first_executed_order = BuyOrderPolygon.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    if sell_filled_already < sell_fillers:
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(sell_prices)
        new_sell_order = SellOrderPolygon(order_id=order_id, token=token_instance, captured_price=0,
                                          price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_sell_order.save()
        new_chart_data = ChartDataPolygon(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()
    else:
        sell_executed_already = len(SellOrderPolygon.objects.filter(
            token=token_instance, executed=True, real=False))

        if sell_executed_already < 15:
            first_order = SellOrderPolygon.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            first_executed_order = SellOrderPolygon.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    return JsonResponse({'success': True})


def polygon_generate_unique_trade_id():
    all_trade_ids = TradeIDPolygon.objects.all()

    id_ = None
    if len(all_trade_ids) == 0:
        id_ = 1
    else:
        last_id = TradeIDPolygon.objects.last()
        id_ = last_id.trade_id
        id_ += 1

    new_id = TradeIDPolygon(trade_id=id_)
    new_id.save()

    return id_


# ethereum-views---------

def ethereum_tokens(request, symbol):
    all_tokens = TokenDataEthereum.objects.all()
    if symbol != None and symbol != '':
        if (not TokenEthereum.objects.filter(symbol=symbol).exists()):
            symbol = '_'
    else:
        symbol = '_'

    token_data = ""
    if symbol != '_':
        token = TokenEthereum.objects.get(symbol=symbol)
        token_data = TokenDataEthereum.objects.get(token=token)

    data = {
        'tokens': all_tokens,
        'token_data': token_data
    }
    return render(request, 'main/tokens.html', data)


def ethereum_order_book(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        token = TokenEthereum.objects.get(url_slug=url_slug_, address=address_)
        sellOrders = SellOrderEthereum.objects.filter(
            token=token, executed=False).order_by('-price')
        buyOrders = BuyOrderEthereum.objects.filter(
            token=token, executed=False).order_by('price')

        sell_orders = []
        for order in sellOrders:
            sell = [int(order.price) / 10**18, (int(order.amount) -
                                                int(order.completed)) / 10**int(token.decimals)]
            sell_orders.append(sell)

        buy_orders = []
        for order in buyOrders:
            buy = [int(order.price) / 10**18, (int(order.amount) -
                                               int(order.completed)) / 10**int(token.decimals)]
            buy_orders.append(buy)

        price = TokenDataEthereum.objects.get(token=token).current_price
        return JsonResponse({'order_book': {'sell_orders': sell_orders, 'buy_orders': buy_orders, 'current_price': price}})


def ethereum_recent_trades(request, address_):
    tokenInstance = TokenEthereum.objects.get(address=address_)
    buyOrders = BuyOrderEthereum.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')
    sellOrders = SellOrderEthereum.objects.filter(
        token=tokenInstance, executed=True).order_by('-timestamp')

    sell_orders = []
    for order in sellOrders:
        sell = [int(order.price) / 10**18, int(order.completed) /
                10**int(tokenInstance.decimals)]
        sell_orders.append(sell)

    buy_orders = []
    for order in buyOrders:
        buy = [int(order.price) / 10**18, int(order.completed) /
               10**int(tokenInstance.decimals)]
        buy_orders.append(buy)

    return JsonResponse({'result': {'buy_trades': buy_orders, 'sell_trades': sell_orders}})


def ethereum_order_history(request, address_, url_slug_, address):
    tokenInstance = TokenEthereum.objects.get(
        url_slug=url_slug_, address=address_)
    token_buys = BuyOrderEthereum.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_sells = SellOrderEthereum.objects.filter(
        user=address, token=tokenInstance).order_by('-timestamp')
    token_buys = serializers.serialize('json', token_buys)
    token_sells = serializers.serialize('json', token_sells)

    # ALL-PAIRS
    buy_orders = BuyOrderEthereum.objects.filter(
        user=address).order_by('-timestamp')
    sell_orders = SellOrderEthereum.objects.filter(
        user=address).order_by('-timestamp')
    all_buys = []
    all_sells = []
    for order in buy_orders:
        buy = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
               order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_buys.append(buy)

    for order in sell_orders:
        sell = [int(order.price)/10**18, int(order.amount)/10**int(order.token.decimals),
                order.token.symbol, order.timestamp, order.executed, order.order_id]
        all_sells.append(sell)

    return JsonResponse({'result': {'current_buy_orders': token_buys, 'current_sell_orders': token_sells, 'all_buys': all_buys, 'all_sells': all_sells}})


def ethereum_home(request, address_, url_slug_):
    if (len(url_slug_) == 0):
        return HttpResponse("NOT A VALID TOKEN")
    else:
        all_tokens = TokenEthereum.objects.filter(valid=True)
        all_tokens_data = TokenDataEthereum.objects.all()
        token = TokenEthereum.objects.get(url_slug=url_slug_, address=address_)
        tokenData = TokenDataEthereum.objects.get(token=token)
        sellOrders = SellOrderEthereum.objects.filter(
            token=token, executed=False).order_by('price')
        buyOrders = BuyOrderEthereum.objects.filter(
            token=token, executed=False).order_by('-price')
        all_price = []
        for order in sellOrders:
            all_price.append(int(order.price))
        if (len(all_price) != 0):
            price = min(all_price)
        else:
            price = 0

        current_datetime = timezone.now()
        datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

        day_volume_ = 0
        day_volume_usd_ = 0
        day_high = 0
        day_low = 0

        new_tokens_all = TokenEthereum.objects.filter(
            valid=True).order_by('-listed_on')
        new_tokens = []
        count = 0
        for token_ in new_tokens_all:
            if count < 10:
                new_tokens.append(token_)
                count += 1

        tokenData.day_volume = int(day_volume_)
        tokenData.day_volume_usd = int(day_volume_usd_)
        tokenData.save()

        day_volume_ += float(tokenData.unreal_volume)
        day_volume_usd_ += float(tokenData.unreal_volume_usd)
        print(day_volume_)

        trending_tokens = []
        all_token_data = TokenDataEthereum.objects.all().annotate(day_volume_int=Cast(
            'day_volume', output_field=IntegerField())).order_by('day_volume_int')
        count = 0
        for token_ in all_token_data:
            if count < 10:
                trending_tokens.append(token_.token)
                count += 1
        mode = request.GET.get('mode')
        data = {
            "allTokens": all_tokens_data,
            "token": token,
            "tokenData": tokenData,
            "sellOrders": sellOrders,
            "buyOrders": buyOrders,
            "current_price": price,
            "day_volume": day_volume_,
            "day_volume_usd": day_volume_usd_,
            "day_high": day_high,
            "day_low": day_low,
            "url_slug": url_slug_,
            "new_tokens": new_tokens,
            "trending_tokens": trending_tokens,
            "chain": 'ethereum',
            "currency": 'ETH',
            "default_icon": '/static/main/images/ether.png',
            "explorer": 'https://ethersan.io',
            "mode": mode
        }

        if (not token.valid):
            return redirect('/')

        return render(request, 'main/home.html', data)


def ethereum_day_volumes(request, address):
    token = TokenEthereum.objects.get(address=address)
    tokenData = TokenDataEthereum.objects.get(token=token)
    sellOrders = SellOrderEthereum.objects.filter(
        token=token, executed=False).order_by('price')
    buyOrders = BuyOrderEthereum.objects.filter(
        token=token, executed=False).order_by('-price')
    price = tokenData.current_price
    current_datetime = timezone.now()
    datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

    day_volume_ = 0
    day_volume_usd_ = 0
    day_high = 0
    day_low = 0
    day_sell_orders = SellOrderEthereum.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    day_buy_orders = BuyOrderEthereum.objects.filter(
        token=token, timestamp__gte=datetime_24_hours_ago)
    for order in day_sell_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)
    for order in day_buy_orders:
        day_volume_ += int(order.amount)
        day_volume_usd_ += (int(order.amount) / 10 **
                            int(token.decimals)) * int(order.price)

    if (len(day_sell_orders) > 0):
        day_high = int(day_sell_orders[0].price)
        day_low = int(day_sell_orders[0].price)
        for order in day_sell_orders:
            if int(order.price) > day_high:
                day_high = int(order.price)
            if int(order.price) < day_low:
                day_low = int(order.price)
    else:
        day_high = price
        day_low = price

    if float(day_volume_) > float(tokenData.day_volume):
        tokenData.day_volume = day_volume_
    if float(day_volume_usd_) > float(tokenData.day_volume_usd):
        tokenData.day_volume_usd = day_volume_usd_

    day_volume_ = tokenData.day_volume
    day_volume_usd_ = tokenData.day_volume_usd
    tokenData.save()
    if (tokenData.market_make):
        day_volume_ = float(tokenData.unreal_volume) + \
            float(tokenData.day_volume)
        day_volume_usd_ = float(tokenData.unreal_volume_usd) + \
            float(tokenData.day_volume_usd)

     # collecting burn amount

    completed_orders = 0
    for order in buyOrders:
        completed_orders += int(order.completed)
    for order in sellOrders:
        completed_orders += int(order.completed)

    burned = completed_orders / 10 ** int(token.decimals)
    burned = (0.07 / 100) * burned

    return JsonResponse({'day_data': {'volume': day_volume_, 'volume_usd': day_volume_usd_, 'day_high': day_high, 'day_low': day_low, 'burned': burned}})


def ethereum_list_token(request):
    if request.method == 'POST':

        address = request.POST.get('address')
        name = request.POST.get('name')
        symbol = request.POST.get('symbol')
        decimals = request.POST.get('decimals')
        user = request.POST.get('user')
        icon_url = request.POST.get('icon_url')
        symbol_ = ''
        valid = "abcdefghijklmnopqrstuvwxyz0123456789"
        for char in symbol:
            if char.lower() not in valid:
                symbol_ += "_"
            else:
                symbol_ += char
        symbol = symbol
        url_slug = symbol + '_USD'

        new_token = TokenEthereum(url_slug=url_slug, address=address, name=name,
                                  symbol=symbol, decimals=decimals, listed_by=user, icon_url=icon_url)
        new_token.save()

        token = TokenEthereum.objects.get(url_slug=url_slug)
        new_data = TokenDataEthereum(token=token, current_price=0,
                                     amount_to_sell=0, amount_to_buy=0)
        new_data.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_get_market_sell(request, token):
    sellOrders = SellOrderEthereum.objects.filter(
        token=token, executed=False).order_by('price')

    id_list = []
    if (len(sellOrders) != 0):
        price = int(sellOrders[0].price)
        for order in sellOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def ethereum_get_market_buy(request, token):
    tokenInstance = TokenEthereum.objects.get(address=token)
    buyOrders = BuyOrderEthereum.objects.filter(
        token=tokenInstance, executed=False).order_by('price')

    id_list = []
    if (len(buyOrders) != 0):
        price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) < price:
                price = int(order.price)
                id_list.append(order.order_id)

    return JsonResponse({'orders': id_list})


def ethereum_get_max_buy_price(request, token):
    tokenInstance = TokenEthereum.objects.get(address=token)
    buyOrders = BuyOrderEthereum.objects.filter(
        token=tokenInstance, executed=False).order_by('price')
    if (len(buyOrders) != 0):
        max_price = int(buyOrders[0].price)
        for order in buyOrders:
            if int(order.price) > max_price:
                max_price = int(order.price)
    else:
        max_price = -1
    return JsonResponse({'max_price': max_price})


def ethereum_check_sell_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = TokenEthereum.objects.get(address=address_)
        orders = SellOrderEthereum.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) <= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_check_buy_order(request, address_, price):
    if request.method == 'GET':
        tokenInstance = TokenEthereum.objects.get(address=address_)
        orders = BuyOrderEthereum.objects.filter(
            token=tokenInstance, executed=False, real=True)
        id_list = []
        for order in orders:
            if int(order.price) >= int(price):
                id_list.append(order.order_id)
        return JsonResponse({'orders': id_list})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_place_buy_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = TokenEthereum.objects.get(address=token)

        found_orders = SellOrderEthereum.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) <= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True
        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_buy = int(amount)
            for id_ in orders:
                order = SellOrderEthereum.objects.get(order_id=id_)
                if int(order.price) <= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_buy > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_buy >= amount_check:
                        amount_to_buy -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_buy < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_buy)
                        amount_to_buy = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_buy <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_buy_order = BuyOrderEthereum(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                         price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_buy_order.save()

        # checking for any price updates
        token_data = TokenDataEthereum.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartDataEthereum(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrderEthereum.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            else:
                all_price = []
                buyOrders = BuyOrderEthereum.objects.filter(
                    token=tokenInstance, executed=False)
                for order in buyOrders:
                    all_price.append(int(order.price))
                if (len(all_price) != 0):
                    price_ = max(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartDataEthereum(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_place_sell_order(request):
    if request.method == 'POST':

        order_id = request.POST.get('order_id')
        token = request.POST.get('token')
        captured_price = request.POST.get('captured_price')
        amount = request.POST.get('amount')
        price = request.POST.get('price')
        user = request.POST.get('user')

        tokenInstance = TokenEthereum.objects.get(address=token)

        found_orders = BuyOrderEthereum.objects.filter(
            token=tokenInstance, executed=False)
        orders = []
        for order in found_orders:
            if int(order.price) >= int(price):
                orders.append(order.order_id)

        completed = 0
        executed = False
        can_revoke = True

        traded__ = False
        if (len(orders) != 0):
            traded__ = True
            amount_to_sell = int(amount)
            for id_ in orders:
                order = BuyOrderEthereum.objects.get(order_id=id_)
                print(order.price, "---------")
                print(price, "---------")
                if int(order.price) >= int(price) and not order.executed and int(order.completed) < int(order.amount) and amount_to_sell > 0:
                    amount_check = int(order.amount) - int(order.completed)
                    if amount_to_sell >= amount_check:
                        amount_to_sell -= amount_check
                        order.completed = order.amount
                        order.executed = True
                        order.can_revoke = False
                        completed += amount_check
                        order.save()
                    elif amount_to_sell < amount_check:
                        order.completed = str(
                            int(order.completed) + amount_to_sell)
                        amount_to_sell = 0
                        completed = amount
                        executed = True
                        can_revoke = False
                        order.save()
                if amount_to_sell <= 0:
                    break

        if (int(amount) == int(completed)):
            can_revoke = False
            executed = True

        new_sell_order = SellOrderEthereum(order_id=order_id, token=tokenInstance, captured_price=captured_price,
                                           price=price, amount=amount, user=user, completed=completed, executed=executed, can_revoke=can_revoke, timestamp=datetime.now(), trade_id=generate_unique_trade_id())
        new_sell_order.save()

        # checking for any price updates
        token_data = TokenDataEthereum.objects.get(token=tokenInstance)
        if traded__:
            token_data.current_price = str(price)

            new_chart_data = ChartDataEthereum(
                token=tokenInstance, price=int(price)/10**18)
            new_chart_data.save()
        else:
            all_price = []
            price_ = 0
            sellOrders = SellOrderEthereum.objects.filter(
                token=tokenInstance, executed=False)
            for order in sellOrders:
                all_price.append(int(order.price))
            if (len(all_price) != 0):
                price_ = min(all_price)
            token_data.current_price = str(price_)

            new_chart_data = ChartDataEthereum(
                token=tokenInstance, price=int(price_)/10**18)
            new_chart_data.save()

        token_data.save()
        # ---------------------------------

        return JsonResponse({'success': True})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_revoke_buy_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (BuyOrderEthereum.objects.filter(order_id=order_id).exists()):
            order = BuyOrderEthereum.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def ethereum_revoke_sell_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        if (SellOrderEthereum.objects.filter(order_id=order_id).exists()):
            order = SellOrderEthereum.objects.get(order_id=order_id)
            if (not order.executed):
                order.delete()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})


def ethereum_new_order_id(request):
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderIDEthereum.objects.filter(order_id=bit).exists()):
            new_id = OrderIDEthereum(order_id=bit)
            new_id.save()
            exist = False
            return JsonResponse({'new_id': bit})


def ethereum_new_order_id_internal():
    random_bit = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    exist = True
    while exist:
        bit = ''
        for i in range(1, random.randint(4, 15)):
            bit += random.choice(random_bit)
        if (not OrderIDEthereum.objects.filter(order_id=bit).exists()):
            new_id = OrderIDEthereum(order_id=bit)
            new_id.save()
            exist = False
            return bit


def ethereum_play_chart(request):
    return render(request, 'main/chart.html')


def ethereum_chart(request, address_):
    # Query to group data by date and calculate OHLC values
    token_instance = TokenEthereum.objects.get(address=address_)
    available_dates = ChartDataEthereum.objects.filter(token=token_instance).values_list(
        'timestamp__date', flat=True).distinct()

    chart_data = []
    for entry_date in available_dates:
        data_for_day = ChartDataEthereum.objects.filter(
            token=token_instance, timestamp__date=entry_date)
        high = data_for_day.aggregate(Max('price'))['price__max']
        low = data_for_day.aggregate(Min('price'))['price__min']
        open_price = data_for_day.earliest('timestamp').price
        close_price = data_for_day.latest('timestamp').price

        chart_data.append({
            'time': entry_date,
            'open': int(open_price),
            'high': int(high),
            'low': int(low),
            'close': int(close_price),
        })

    return JsonResponse(chart_data, safe=False)


def ethereum_control(request):
    return render(request, 'main/control.html')


def ethereum_number_of_listed_tokens(request, address_):
    listed_tokens = TokenEthereum.objects.filter(listed_by=address_)
    number = len(listed_tokens)
    return JsonResponse({'listed': number})


def ethereum_all_listed_tokens(request):
    all_tokens = TokenEthereum.objects.filter(valid=True)
    all_tokens = serializers.serialize("json", all_tokens)
    return JsonResponse({'all_tokens': all_tokens})


def ethereum_market_maker(request):
    if request.method == 'POST':
        token_address = request.POST.get('market-make-address')
        volume = request.POST.get('market-make-volume')
        user_address = request.POST.get('user-address')
        market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'
        if user_address != market_maker:
            return JsonResponse({'success': False, 'error': 'Invalid Market Maker Address'})

        volume = int(volume)
        token = TokenEthereum.objects.get(address=token_address)
        decimals = token.decimals
        actual_volume = volume * 10 ** int(decimals)
        print(actual_volume)
        per_order_amount_max = int(actual_volume / 30)
        percent_deviation = (10 * per_order_amount_max) / 100
        per_order_amount_min = int(per_order_amount_max - percent_deviation)
        current_price = TokenDataEthereum.objects.get(
            token=token).current_price
        current_price = int(current_price)
        price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
        price_deivation = int(price_deivation)

        running_price_sell = current_price + price_deivation
        running_price_buy = current_price - price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_sell_order = SellOrderEthereum(order_id=order_id, token=token, captured_price=0,
                                               price=running_price_sell, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_sell_order.save()
            new_chart_data = ChartDataEthereum(
                token=token, price=int(running_price_sell)/10**18)
            new_chart_data.save()
            running_price_sell = running_price_sell + price_deivation

        for i in range(10):
            amount = random.randint(per_order_amount_min, per_order_amount_max)
            order_id = new_order_id_internal()
            new_buy_order = BuyOrderEthereum(order_id=order_id, token=token, captured_price=0,
                                             price=running_price_buy, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
            new_buy_order.save()
            new_chart_data = ChartDataEthereum(
                token=token, price=int(running_price_buy)/10**18)
            new_chart_data.save()
            running_price_buy = running_price_buy - price_deivation

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def ethereum_auto_market_maker(request, token):
    token_instance = TokenEthereum.objects.get(address=token)
    token_data = TokenDataEthereum.objects.get(token=token_instance)
    market_maker = '0x525C374d5F652d4091a931D46321d909C96d647b'

    if not token_data.market_make:
        return JsonResponse({'success': False, 'error': 'Market Maker is not enabled for this Token'})

    volume = int(token_data.market_make_volume) * \
        10 ** int(token_instance.decimals)
    sell_fillers = int(token_data.sell_fillers)
    buy_fillers = int(token_data.buy_fillers)
    current_price = int(token_data.current_price)

    per_order_amount = int(volume / 30)
    percent_deviation = (20 * per_order_amount) / 100
    per_order_amount_max = int(per_order_amount + percent_deviation)
    per_order_amount_min = int(per_order_amount - percent_deviation)

    price_deivation = '1' + '0' * int(len(str(current_price)) - 3)
    price_deivation = int(price_deivation)

    running_price_sell = current_price + price_deivation
    running_price_buy = current_price - price_deivation

    sell_prices = []
    buy_prices = []

    for _ in range(sell_fillers):
        sell_prices.append(running_price_sell)
        running_price_sell += price_deivation

    for _ in range(buy_fillers):
        buy_prices.append(running_price_buy)
        running_price_buy -= price_deivation

    buy_filled_already = len(BuyOrderEthereum.objects.filter(
        token=token_instance, executed=False, real=False))
    sell_filled_already = len(SellOrderEthereum.objects.filter(
        token=token_instance, executed=False, real=False))

    if buy_filled_already < buy_fillers:
        print(1)
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(buy_prices)
        new_buy_order = BuyOrderEthereum(order_id=order_id, token=token_instance, captured_price=0,
                                         price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_buy_order.save()
        new_chart_data = ChartDataEthereum(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()

        token_data.unreal_volume = float(
            token_data.unreal_volume) + float(amount)
        token_data.unreal_volume_usd = float(token_data.unreal_volume_usd) + (
            (float(amount) / 10 ** int(token_instance.decimals)) * float(price))
        token_data.save()

    else:
        print(2)
        buy_executed_already = len(BuyOrderEthereum.objects.filter(
            token=token_instance, executed=True, real=False))

        if buy_executed_already < 15:
            print(3)
            first_order = BuyOrderEthereum.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            print(4)
            first_executed_order = BuyOrderEthereum.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    if sell_filled_already < sell_fillers:
        amount = random.randint(per_order_amount_min, per_order_amount_max)
        order_id = new_order_id_internal()
        price = random.choice(sell_prices)
        new_sell_order = SellOrderEthereum(order_id=order_id, token=token_instance, captured_price=0,
                                           price=price, amount=amount, user=market_maker, completed=0, executed=False, can_revoke=True, timestamp=datetime.now(), real=False, trade_id=generate_unique_trade_id())
        new_sell_order.save()
        new_chart_data = ChartDataEthereum(
            token=token_instance, price=int(price)/10**18, real=False)
        new_chart_data.save()
    else:
        sell_executed_already = len(SellOrderEthereum.objects.filter(
            token=token_instance, executed=True, real=False))

        if sell_executed_already < 15:
            first_order = SellOrderEthereum.objects.filter(
                token=token_instance, executed=False, real=False).first()
            first_order.executed = True
            first_order.completed = first_order.amount
            first_order.save()
        else:
            first_executed_order = SellOrderEthereum.objects.filter(
                token=token_instance, executed=True, real=False).first()
            first_executed_order.delete()

    return JsonResponse({'success': True})


def ethereum_generate_unique_trade_id():
    all_trade_ids = TradeIDEthereum.objects.all()

    id_ = None
    if len(all_trade_ids) == 0:
        id_ = 1
    else:
        last_id = TradeIDEthereum.objects.last()
        id_ = last_id.trade_id
        id_ += 1

    new_id = TradeIDEthereum(trade_id=id_)
    new_id.save()

    return id_


# API endpoints

def pairs(request):
    all_tokens = Token.objects.all()
    pairs = []
    for token in all_tokens:
        pair = {"ticker_id": token.url_slug,
                "base": token.symbol, "target": 'USD'}
        pairs.append(pair)

    return JsonResponse(pairs, safe=False)


def tickers(request):
    all_tokens = Token.objects.all()
    tickers = []
    for token in all_tokens:
        tokenData = TokenData.objects.get(token=token)
        bid = 0
        buy_orders = BuyOrder.objects.filter(token=token, executed=False)
        for order in buy_orders:
            if int(order.price) > bid:
                bid = int(order.price)
        ask = 0
        sell_orders = SellOrder.objects.filter(token=token, executed=False)
        if len(sell_orders) != 0:
            ask = int(sell_orders[0].price)
            for order in sell_orders:
                if int(order.price) < ask:
                    ask = int(order.price)

        current_datetime = timezone.now()
        datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=25)

        day_high = 0
        day_low = 0
        day_sell_orders = SellOrder.objects.filter(
            token=token, timestamp__gte=datetime_24_hours_ago)
        day_buy_orders = BuyOrder.objects.filter(
            token=token, timestamp__gte=datetime_24_hours_ago)

        if (len(day_sell_orders) > 0):
            day_high = int(day_sell_orders[0].price)
            day_low = int(day_sell_orders[0].price)
            for order in day_sell_orders:
                if int(order.price) > day_high:
                    day_high = int(order.price)
                if int(order.price) < day_low:
                    day_low = int(order.price)

        ticker = {
            "ticker_id": token.url_slug,
            "base_currency": token.symbol,
            "target_currency": "USD",
            "last_price": str(float(tokenData.current_price) / 10 ** 18),
            "base_volume": str((float(tokenData.day_volume) + float(tokenData.unreal_volume)) / 10 ** float(token.decimals)),
            "target_volume": str((float(tokenData.day_volume_usd) + float(tokenData.unreal_volume_usd)) / 10 ** 18),
            "bid": str(bid / 10 ** 18),
            "ask": str(ask / 10 ** 18),
            "high": str(float(day_high) / 10 ** 18),
            "low": str(float(day_low) / 10 ** 18),
        }
        tickers.append(ticker)

    return JsonResponse(tickers, safe=False)


def orderbook(request):
    ticker_id = request.GET.get('ticker_id')
    depth = request.GET.get('depth')

    if ticker_id == None or ticker_id == '':
        return JsonResponse({'success': False, 'message': 'Mandatory parameter `ticker_id` was not sent, was empty/null, or malformed.'})

    if (not Token.objects.filter(url_slug=ticker_id).exists()):
        return JsonResponse({'success': False, 'message': 'Invalid `ticker_id`'})

    have_depth = False

    if depth != None and depth != '':
        try:
            depth = int(depth)
            have_depth = True
        except:
            return JsonResponse({'success': False, 'message': 'Illegal characters in `depth`'})

    bids = []
    asks = []
    token = Token.objects.get(url_slug=ticker_id)
    tokenData = TokenData.objects.get(token=token)

    buy_orders = BuyOrder.objects.filter(token=token, executed=False)
    sell_orders = SellOrder.objects.filter(token=token, executed=False)

    buy_count = len(buy_orders)
    sell_count = len(sell_orders)

    if (have_depth):
        buy_count = depth
        sell_count = depth

    for order in buy_orders:
        if buy_count > 0:
            bid = [
                str(float(order.price) / 10 ** 18),
                str(float(order.amount) / 10 ** int(token.decimals))
            ]
            bids.append(bid)
            buy_count -= 1

    for order in sell_orders:
        if sell_count > 0:
            ask = [
                str(float(order.price) / 10 ** 18),
                str(float(order.amount) / 10 ** int(token.decimals))
            ]
            asks.append(ask)
            sell_count -= 1

    orderbook = {
        "ticker_id": ticker_id,
        "timestamp": int(timezone.now().timestamp()),
        "bids": bids,
        "asks": asks
    }

    return JsonResponse(orderbook)

# | API endpoint - /historical_trades


def historical_trades(request):
    ticker_id = request.GET.get('ticker_id')
    type = request.GET.get('type')

    if ticker_id == None or ticker_id == '':
        return JsonResponse({'success': False, 'message': 'Mandatory parameter `ticker_id` was not sent, was empty/null, or malformed.'})

    if (not Token.objects.filter(url_slug=ticker_id).exists()):
        return JsonResponse({'success': False, 'message': 'Invalid `ticker_id`'})

    have_type = False

    if type != None and type != '':
        if type != 'buy' and type != 'sell':
            return JsonResponse({'success': False, 'message': 'Invalid `type`'})
        else:
            have_type = True

    buy_trades = []
    sell_trades = []

    token = Token.objects.get(url_slug=ticker_id)
    tokenData = TokenData.objects.get(token=token)

    all_buy_trades = BuyOrder.objects.filter(token=token, executed=True)
    all_sell_trades = SellOrder.objects.filter(token=token, executed=True)

    for trade in all_buy_trades:
        price = float(trade.price) / 10 ** 18
        amount = float(trade.amount) / 10 ** int(token.decimals)
        buy = {
            "trade_id": trade.trade_id,
            "price": str(price),
            "base_volume": str(amount),
            "target_volume": str(amount * price),
            "trade_timestamp": str(int(trade.timestamp.timestamp())),
            "type": "buy"
        }
        buy_trades.append(buy)

    for trade in all_sell_trades:
        price = float(trade.price) / 10 ** 18
        amount = float(trade.amount) / 10 ** int(token.decimals)
        sell = {
            "trade_id": trade.trade_id,
            "price": str(price),
            "base_volume": str(amount),
            "target_volume": str(amount * price),
            "trade_timestamp": str(int(trade.timestamp.timestamp())),
            "type": "sell"
        }
        sell_trades.append(sell)

    if not have_type:
        return JsonResponse({"buy": buy_trades, "sell": sell_trades})
    else:
        if type == 'sell':
            return JsonResponse({"sell": sell_trades})
        elif type == 'buy':
            return JsonResponse({"buy": buy_trades})

    return JsonResponse({"success": False, "message": "Invalid query!"})
