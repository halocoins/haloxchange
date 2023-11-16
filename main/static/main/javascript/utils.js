var truncateRegex = /^(0x[a-zA-Z0-9]{4})[a-zA-Z0-9]+([a-zA-Z0-9]{4})$/;

var truncateEthAddress = function (address) {
    var match = address.match(truncateRegex);
    if (!match)
        return address;
    return match[1] + "\u2026" + match[2];
};

const getWeb3 = async (wallet, injected) => {
    closeWallet();
    return new Promise(async (resolve, reject) => {

        if (!injected) {
            var provider = await window.ethProvider();
            // provider.chainId = 56;
            provider.enable().then(function (res) {
                web3 = new Web3(provider);
                localStorage.setItem('walletProvider', 'walletconnect');
                resolve(web3)
            });
        }
        else {
            if (typeof window.ethereum !== "undefined") {
                try {
                    let provider = window.ethereum;
                    // edge case if MM and CBW are both installed
                    if (wallet === "metamask") {
                        provider = window.ethereum;
                        await provider.request({
                            method: "eth_requestAccounts",
                            params: [],
                        });
                    }
                    else if (wallet === "coinbase") {
                        if (window.ethereum.providers?.length) {
                            window.ethereum.providers.forEach(async (p) => {
                                if (p.isCoinbaseWallet) provider = p;
                            });
                        }
                        await provider.request({
                            method: "eth_requestAccounts",
                            params: [],
                        });
                    }
                    else if (wallet === "trustwallet") {
                        provider = window.trustwallet;
                        await provider.request({
                            method: "eth_requestAccounts",
                            params: [],
                        });
                    }
                    else if (wallet === "enkrypt") {
                        provider = window.enkrypt;
                        await provider.enable();
                    }
                    else {
                        provider = window.ethereum;
                    }
                    web3 = new Web3(provider);
                    localStorage.setItem('walletProvider', wallet);
                    resolve(web3);
                } catch (error) {
                    console.log(error)
                    openGlobalError("Wallet not installed", 5000)
                }

            }
        }


    });
}



const getTokenContract = async (web3, address) => {
    const tokenContract = new web3.eth.Contract(tokenAbi, address);
    return tokenContract;
};

const getContract = async (web3) => {
    const contract = new web3.eth.Contract(contractABI, contractAddress);
    return contract;
}

var bnbPrice = 0;


const updateBNBprice1 = async () => {
    try {
        let response = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${symbol}USDT`);
        let data = await response.json();
        bnbPrice = Number(data['price']);
    } catch (error) {
        console.log("Failed to Fetch BNB Price from API-1, Tryping API-2")
        updateBNBprice2();
    }
}

const updateBNBprice2 = async () => {
    try {
        let sym = 'binancecoin';
        if (symbol === "BNB") {
            sym = 'binancecoin';
        }
        else if (symbol === 'MATIC') {
            sym = 'matic-network';
        }
        else if (symbol === 'ETH') {
            sym = 'ethereum';
        }
        let response = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${sym}&vs_currencies=usd`);
        let data = await response.json();
        bnbPrice = Number(data['price']);
    } catch (error) {
        console.log("Failed to Fetch BNB Price from API-2, Trying API-3")
        updateBNBprice3();
    }
}


const updateBNBprice3 = async () => {
    try {
        let response = await fetch(`/fetch_currency_price/${symbol}/`);
        let data = await response.json();
        bnbPrice = Number(data['price']);
    } catch (error) {
        console.log("Failed to Fetch BNB Price from API-3, Exiting");
    }
}

const updateBNBPrice = async () => {
    updateBNBprice3();
}


$(document).ready(async function () {
    await new Promise(r => setTimeout(r, 1000));
    updateBNBPrice();
    setInterval(updateBNBPrice, 15000);
});

const getBNBPrice = async () => {
    return Number(bnbPrice);
}

const checkSellOrders = async (address, price) => {
    let response = await fetch(`/${chainSlug}/check_sell_orders/` + address + '/' + price + '/');
    let data = await response.json();
    return data.orders;
}
const checkBuyOrders = async (address, price) => {
    let response = await fetch(`/${chainSlug}/check_buy_orders/` + address + '/' + price + '/');
    let data = await response.json();
    return data.orders;
}

const checkMarketSellOrders = async (address) => {
    let response = await fetch(`/${chainSlug}/get_market_sell/` + address + '/');
    let data = await response.json();
    return data.orders;
}
const checkMarketBuyOrders = async (address) => {
    let response = await fetch(`/${chainSlug}/get_market_buy/` + address + '/');
    let data = await response.json();
    return data.orders;
}

const getMaxBuyPrice = async (address) => {
    let response = await fetch(`/${chainSlug}/get_max_buy_price/` + address + '/');
    let data = await response.json();
    return data.max_price
}

const newOrderID = async () => {
    let response = await fetch(`/${chainSlug}/new_order_id/`)
    let data = await response.json();
    return data.new_id;
}

const getNumberOfListedTokens = async (address_) => {
    let response = await fetch(`/${chainSlug}/api/number_of_listed_tokens/` + address_ + '/')
    let data = await response.json();
    return data.listed;
}

$(document).ready(async function () {
    await new Promise(r => setTimeout(r, 4000));
    updateOrderBook();
    setInterval(updateData, 5000);

    setInterval(autoMarketMake, 10000);
});

async function updateData() {
    if (orderMode == 'book') {
        updateOrderBook();
    } else {
        updateRecentTrades();
    }
    updateBalances();

    if (userAddress) {
        updateOrderHistory();
    }

}

async function updateOrderBook() {
    $.ajax({
        url: `/${chainSlug}/order_book/${token_address}/${url_slug}`,
        dataType: "json",
        success: async function (data) {
            let resultSell = data.order_book.sell_orders
            var html_sell = "";
            for (var i = 0; i < resultSell.length; i++) {
                html_sell += `<div class="orderBookItem sellItem" onclick="fillBuyField(${resultSell[i][0]},${resultSell[i][1]})"><p class="orderPrice">${resultSell[i][0]}</p><p>${resultSell[i][1].toFixed(2)}</p></div>`;
            }
            $("#order-book-sell").html(html_sell);

            let resultBuy = data.order_book.buy_orders
            var html_buy = "";
            for (var i = 0; i < resultBuy.length; i++) {
                html_buy += `<div class="orderBookItem buyItem" onclick="fillSellField(${resultBuy[i][0]},${resultBuy[i][1]})"><p class="orderPrice">${resultBuy[i][0]}</p><p>${resultBuy[i][1].toFixed(2)}</p></div>`;
            }
            $("#order-book-buy").html(html_buy);

            document.getElementById('current-price').innerHTML = data.order_book.current_price / 10 ** 18


        }
    });
}

async function updateRecentTrades() {
    $.ajax({
        url: `/${chainSlug}/recent_trades/${token_address}/`,
        dataType: "json",
        success: async function (data) {
            let resultSell = data.result.sell_trades
            var html_sell = "";
            for (var i = 0; i < resultSell.length; i++) {
                html_sell += `<div class="orderBookItem sellItem" onclick="fillBuyField(${resultSell[i][0]},${resultSell[i][1]})"><p class="orderPrice">${resultSell[i][0]}</p><p>${resultSell[i][1].toFixed(2)}</p></div>`;
            }
            $("#order-transaction-sell").html(html_sell);

            let resultBuy = data.result.buy_trades
            var html_buy = "";
            for (var i = 0; i < resultBuy.length; i++) {
                html_buy += `<div class="orderBookItem buyItem" onclick="fillSellField(${resultBuy[i][0]},${resultBuy[i][1]})"><p class="orderPrice">${resultBuy[i][0]}</p><p>${resultBuy[i][1].toFixed(2)}</p></div>`;
            }
            $("#order-transaction-buy").html(html_buy);

        }
    });
}

async function updateOrderHistory() {
    $.ajax({
        url: `/${chainSlug}/order_history/${token_address}/${url_slug}/${userAddress}`,
        dataType: "json",
        success: async function (data) {
            let resultToken = data.result.current_buy_orders
            resultToken = JSON.parse(resultToken)

            var html_token = "";
            resultToken.forEach(element => {
                let datetime = (element.fields.timestamp).slice(0, 10) + " " + (element.fields.timestamp).slice(11, 16);

                html_token += `<div class="orderHistoryItem historyBuy"><p class="orderMode">${element.fields.price / 10 ** 18}</p><p>${(element.fields.amount / 10 ** decimals_).toFixed(2)}</p><p style='font-size: 8px'>${datetime}</p>`;
                if (element.fields.executed) {
                    html_token += `<a class="complete"><i class="las la-check"></i></a>`
                }
                else {
                    html_token += `<a onclick='revokeBuyOrder("${element.fields.order_id}")' class="revoke"><i class="lar la-times-circle"></i></a>`
                }
                html_token += `</div>`
            });
            $("#order-history-token-buy").html(html_token);

            resultToken = data.result.current_sell_orders
            resultToken = JSON.parse(resultToken)

            var html_token = "";
            resultToken.forEach(element => {
                let datetime = (element.fields.timestamp).slice(0, 10) + " " + (element.fields.timestamp).slice(11, 16);

                html_token += `<div class="orderHistoryItem historySell"><p class="orderMode">${element.fields.price / 10 ** 18}</p><p>${(element.fields.amount / 10 ** decimals_).toFixed(2)}</p><p style='font-size: 8px'>${datetime}</p>`;
                if (element.fields.executed) {
                    html_token += `<a class="complete"><i class="las la-check"></i></a>`
                }
                else {
                    html_token += `<a onclick='revokeSellOrder("${element.fields.order_id}")' class="revoke"><i class="lar la-times-circle"></i></a>`
                }
                html_token += `</div>`
            });
            $("#order-history-token-sell").html(html_token);

            // order-history-------

            resultToken = data.result.all_buys
            var html_token = "";
            for (var i = 0; i < resultToken.length; i++) {
                let datetime = (resultToken[i][3]).slice(0, 10) + " " + (resultToken[i][3]).slice(11, 16);
                html_token += `<div class="orderHistoryItem historyBuy"><p class="orderMode">${resultToken[i][0]}</p><p>${resultToken[i][1].toFixed(2)} ${resultToken[i][2]}</p><p style='font-size: 8px'>${datetime}</p>`
                if (resultToken[i][4]) {
                    html_token += `<a class="complete"><i class="las la-check"></i></a>`
                }
                else {
                    html_token += `<a onclick='revokeBuyOrder("${resultToken[i][5]}")' class="revoke"><i class="lar la-times-circle"></i></a>`
                }
                html_token += `</div>`
            }
            $("#order-history-all-buy").html(html_token);

            resultToken = data.result.all_sells
            var html_token = "";
            for (var i = 0; i < resultToken.length; i++) {
                let datetime = (resultToken[i][3]).slice(0, 10) + " " + (resultToken[i][3]).slice(11, 16);
                html_token += `<div class="orderHistoryItem historySell"><p class="orderMode">${resultToken[i][0]}</p><p>${resultToken[i][1].toFixed(2)} ${resultToken[i][2]}</p><p style='font-size: 8px'>${datetime}</p>`
                if (resultToken[i][4]) {
                    html_token += `<a class="complete"><i class="las la-check"></i></a>`
                }
                else {
                    html_token += `<a onclick='revokeSellOrder("${resultToken[i][5]}")' class="revoke"><i class="lar la-times-circle"></i></a>`
                }
                html_token += `</div>`
            }
            $("#order-history-all-sell").html(html_token);


        }
    });
}

async function returnAllTokens() {
    let response = await fetch(`/exchange/${chainSlug}/all_listed_tokens/`)
    let data = await response.json();
    return data.all_tokens;
}


$(document).ready(async function () {
    await new Promise(r => setTimeout(r, 1000));
    updateVolumes();
    setInterval(updateVolumes, 5000);
});

async function updateVolumes() {
    let response = await fetch(`/${chainSlug}/day_volumes/${token_address}/`)
    let data = await response.json();
    data = data.day_data;
    document.getElementById('day-volume-token').innerHTML = (Number(data.volume) / 10 ** Number(decimals_)).toFixed(2);
    document.getElementById('day-volume-usd').innerHTML = (data.volume_usd / 10 ** 18).toFixed(2);
    document.getElementById('day-high').innerHTML = (data.day_high / 10 ** 18);
    document.getElementById('day-low').innerHTML = (data.day_low / 10 ** 18);
    document.getElementById('burned').innerHTML = (data.burned).toFixed(2);
}

async function autoMarketMake() {
    $.ajax({
        url: `/${chainSlug}/auto_market_maker/${token_address}/`,
        dataType: "json",
        success: async function (data) {
            //    console.log(data) // for development purpose only
        }
    });
}

async function fetchCoinGecko() {
    let response = await fetch('https://tokens.pancakeswap.finance/coingecko.json');
    let data = await response.json();
    data = data.tokens;
    return data
}





async function forceNetworkSwitch(networkId) {
    let providerStorage = localStorage.getItem('walletProvider');
    if (providerStorage) {
        if (providerStorage != 'walletconnect' && providerStorage != 'trustwallet') {
            try {
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: web3.utils.toHex(networkId) }],
                });
                location.reload();
            } catch (error) {
                console.error('Failed to switch network:', error);
            }
        } else {
            console.error('Injected web3 not found');
        }
    }
}



// Blockchain Data
const blockchainData = {
    'bsc': {
        'chainId': 56,
        'chainSlug': 'bsc',
        'networkName': 'Binance Smart Chain',
        'symbol': 'BNB',
        'smartContract': '',
        'logoURL': 'bsc.png',
        'apiKey': '',
        'gasLimit': '280000 ',
        'gasLimitTrans': '550000',
        'gasTracker': 'https://api.bscscan.com/api?module=gastracker&action=gasoracle&apikey=',
        'importURL': '/import_token/',
        'defaultIconURL': '/static/main/images/token.png',
        'tokenList': 'available-token-list-bsc',
    },
    'polygon': {
        'chainId': 137,
        'chainSlug': 'polygon',
        'networkName': 'Polygon Mainnet',
        'symbol': 'MATIC',
        'smartContract': '',
        'logoURL': 'polygon.png',
        'apiKey': '',
        'gasLimit': '450000',
        'gasLimitTrans': '400000',
        'gasTracker': 'https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey=',
        'importURL': '/import_token_polygon/',
        'defaultIconURL': '/static/main/images/polygon.png',
        'tokenList': 'available-token-list-polygon',
    },
    'ethereum': {
        'chainId': 1,
        'chainSlug': 'ethereum',
        'networkName': 'Ethereum Mainnet',
        'symbol': 'ETH',
        'smartContract': '',
        'logoURL': 'ether.png',
        'apiKey': '',
        'gasLimit': '270000',
        'gasLimitTrans': '270000',
        'gasTracker': 'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=',
        'importURL': '/import_token_ethereum/',
        'defaultIconURL': '/static/main/images/ether.png',
        'tokenList': 'available-token-list-ethereum',
    },
}