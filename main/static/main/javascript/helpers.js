function openListToken() {
    document.getElementById('list-token-wrapper').style.display = 'flex';
}
function closeListToken() {
    document.getElementById('list-token-wrapper').style.display = 'none';
    document.getElementById('token-list-address').value = '';
    document.getElementById('list-token-details').style.display = 'none';
    document.getElementById('list-token-btn').disabled = true;
}

function openChangeToken() {
    document.getElementById('change-token-wrapper').style.display = 'flex';
}
function closeChangeToken() {
    document.getElementById('change-token-wrapper').style.display = 'none';
    document.getElementById('change-token-input').value = '';
    document.getElementById('not-found').style.display = 'none';

}

function openChangeCurrency() {
    document.getElementById('change-currency-wrapper').style.display = 'flex';
}
function closeChangeCurrency() {
    document.getElementById('change-currency-wrapper').style.display = 'none';

}
function openChangeTheme() {
    document.getElementById('change-theme-wrapper').style.display = 'flex';
}
function closeChangeTheme() {
    document.getElementById('change-theme-wrapper').style.display = 'none';
}
function openExchangePop() {
    document.getElementById('exchange-pop').style.display = 'flex';
}
function closeExchangePop() {
    document.getElementById('exchange-pop').style.display = 'none';
    localStorage.setItem("exchange-pop", true)
}

function openClaimReward() {
    document.getElementById('claim-reward-wrapper').style.display = 'flex';
}
function closeClaimReward() {
    document.getElementById('claim-reward-wrapper').style.display = 'none';
    document.getElementById('claim-listed-tokens').innerHTML = '0';
    document.getElementById('claim-listed-reward').innerHTML = '0';
}

function openListingLoader() {
    document.getElementById('listing-token-prompt').style.display = 'flex';
}
function closeListingLoader() {
    document.getElementById('listing-token-prompt').style.display = 'none';
}

async function openGlobalInfo(message, time) {
    document.getElementById('info').innerHTML = message;
    document.getElementById('global-message').style.display = 'block';
    await new Promise(r => setTimeout(r, time));
    document.getElementById('info').innerHTML = '';
    document.getElementById('global-message').style.display = 'none';
}

async function openGlobalError(message, time) {
    document.getElementById('error').innerHTML = message;
    document.getElementById('global-error').style.display = 'block';
    await new Promise(r => setTimeout(r, time));
    document.getElementById('error').innerHTML = '';
    document.getElementById('global-error').style.display = 'none';
}

async function displayBuyConversion(text, time) {
    document.getElementById('buy-conversion-text').innerHTML = text;
    document.getElementById('buy-conversion-text').style.display = 'block';
    await new Promise(r => setTimeout(r, time));
    document.getElementById('buy-conversion-text').style.display = 'none';
    document.getElementById('buy-conversion-text').innerHTML = '';
}
async function displaySellConversion(text, time) {
    document.getElementById('sell-conversion-text').innerHTML = text;
    document.getElementById('sell-conversion-text').style.display = 'block';
    await new Promise(r => setTimeout(r, time));
    document.getElementById('sell-conversion-text').style.display = 'none';
    document.getElementById('sell-conversion-text').innerHTML = '';
}

function openBuyError(text) {
    document.getElementById('error-text-buy').innerHTML = text;
    document.getElementById('error-text-buy').style.display = 'block';
}
function closeBuyError() {
    document.getElementById('error-text-buy').innerHTML = '';
    document.getElementById('error-text-buy').style.display = 'none';
}

function openSellError(text) {
    document.getElementById('error-text-sell').innerHTML = text;
    document.getElementById('error-text-sell').style.display = 'block';
}
function closeSellError() {
    document.getElementById('error-text-sell').innerHTML = '';
    document.getElementById('error-text-sell').style.display = 'none';
}

function openWallet() {
    if (userAddress) {
        openWalletDis();
    }
    else {
        document.getElementById('wallet-container').style.display = 'flex';
    }
}

function closeWallet() {
    document.getElementById('wallet-container').style.display = 'none';
}

function openWalletDis() {
    document.getElementById('wallet-disconnect').style.display = 'flex';
}

function closeWalletDis() {
    document.getElementById('wallet-disconnect').style.display = 'none';
}

function fillBuyField(price, amount) {
    if (tradeMode != 'market') {
        document.getElementById('buy-price-input').value = price;
        document.getElementById('buy-amount-input').value = amount;
        validateBuyAmount();
    }
}

function fillSellField(price, amount) {
    if (tradeMode != 'market') {
        document.getElementById('sell-price-input').value = price;
        document.getElementById('sell-amount-input').value = amount;
        validateSellAmount();
    }
}

function switchTokenHistory() {
    document.getElementById('order-history-all').style.display = 'none';
    document.getElementById('order-history-current').style.display = 'flex';
    document.getElementById('current-pair-switch').style.background = 'orange';
    document.getElementById('current-pair-switch').style.color = 'black';
    document.getElementById('all-pair-switch').style.background = 'rgb(60,60,60)';
    document.getElementById('all-pair-switch').style.color = 'gray';
    historyMode = 'current';
}
function switchAllHistory() {
    document.getElementById('order-history-all').style.display = 'flex';
    document.getElementById('order-history-current').style.display = 'none';
    document.getElementById('current-pair-switch').style.background = 'rgb(60,60,60)';
    document.getElementById('current-pair-switch').style.color = 'gray';
    document.getElementById('all-pair-switch').style.background = 'orange';
    document.getElementById('all-pair-switch').style.color = 'black';
    historyMode = 'all';
}
function switchOrderActive() {
    document.getElementById('order-book-transactions').style.display = 'none';
    document.getElementById('order-book-active').style.display = 'flex';
    document.getElementById('order-book-switch').style.background = 'orange';
    document.getElementById('order-book-switch').style.color = 'black';
    document.getElementById('order-transaction-switch').style.background = 'rgb(60,60,60)';
    document.getElementById('order-transaction-switch').style.color = 'gray';
    orderMode = 'book';
}
function switchOrderTransactions() {
    document.getElementById('order-book-active').style.display = 'none';
    document.getElementById('order-book-transactions').style.display = 'flex';
    document.getElementById('order-transaction-switch').style.background = 'orange';
    document.getElementById('order-transaction-switch').style.color = 'black';
    document.getElementById('order-book-switch').style.background = 'rgb(60,60,60)';
    document.getElementById('order-book-switch').style.color = 'gray';
    orderMode = 'trades';
}


let changeOpen = true

function toggleNetworkChange() {
    if (changeOpen) {
        changeOpen = false;
        document.getElementById('network-change-box').style.display = 'none';
    }
    else {
        changeOpen = true;
        document.getElementById('network-change-box').style.display = 'flex';
    }
}


function changeNetwork(chain_slug, reload) {
    chain = chain_slug;
    localStorage.setItem('network', chain);
    updateChainData();
    document.getElementById('network-icon').setAttribute('src', `/static/main/images/chains/${logoURL}`)
    document.getElementById('network-name').innerHTML = networkName; 
    if (reload) {
        location.reload();
    }
}

function changeNetworkURL (chain_slug) {
    window.location.replace(`/exchange/${chain_slug}/`)
}


function changeTradeModeTo(mode) {
    if (mode == 'limit') {
        tradeMode = 'limit';
        document.getElementById('market-mode').style.background = 'rgb(60,60,60)';
        document.getElementById('market-mode').style.color = 'gray';
        document.getElementById('limit-mode').style.background = 'orange';
        document.getElementById('limit-mode').style.color = 'black';
        document.getElementById('buy-price-input').style.background = 'rgb(30,30,30)';
        document.getElementById('sell-price-input').style.background = 'rgb(30,30,30)';
        document.getElementById('buy-price-input').style.cursor = 'text';
        document.getElementById('sell-price-input').style.cursor = 'text';
        document.getElementById('buy-price-input').removeAttribute('readonly')
        document.getElementById('sell-price-input').removeAttribute('readonly')
    }
    else if (mode == 'market') {
        tradeMode = 'market';
        document.getElementById('limit-mode').style.background = 'rgb(60,60,60)';
        document.getElementById('limit-mode').style.color = 'gray';
        document.getElementById('market-mode').style.background = 'orange';
        document.getElementById('market-mode').style.color = 'black';
        document.getElementById('buy-price-input').value = '';
        document.getElementById('sell-price-input').value = '';
        document.getElementById('buy-price-input').style.background = 'rgb(100,100,100)';
        document.getElementById('sell-price-input').style.background = 'rgb(100,100,100)';
        document.getElementById('buy-price-input').style.cursor = 'default';
        document.getElementById('sell-price-input').style.cursor = 'default';
        document.getElementById('buy-price-input').setAttribute('readonly', true)
        document.getElementById('sell-price-input').setAttribute('readonly', true)
    }
    else {
        tradeMode = 'limit';
    }
}

function openMobileTop() {
    document.getElementById('mobile-top-switch-close').style.display = 'flex';
    document.getElementById('mobile-top-switch-open').style.display = 'none';
    document.getElementById('mobile-top-options').style.display = 'flex';
}
function closeMobileTop() {
    document.getElementById('mobile-top-switch-close').style.display = 'none';
    document.getElementById('mobile-top-switch-open').style.display = 'flex';
    document.getElementById('mobile-top-options').style.display = 'none';
}

var root = document.querySelector(':root');
function changeTheme(theme) {
    if (theme == 1) {
        root.style.setProperty('--sell', 'orange');
        root.style.setProperty('--buy', 'rgb(0, 150, 255)');
        localStorage.setItem("theme-sell", "orange");
        localStorage.setItem("theme-buy", "rgb(0, 150, 255)");
        closeChangeTheme();
    }
    else if (theme == 2) {
        root.style.setProperty('--sell', '#ae1414');
        root.style.setProperty('--buy', '#128a52');
        localStorage.setItem("theme-sell", "#ae1414");
        localStorage.setItem("theme-buy", "#128a52");
        closeChangeTheme();
    }
    else if (theme == 3) {
        root.style.setProperty('--sell', 'rgb(219, 0, 0)');
        root.style.setProperty('--buy', 'rgb(0, 189, 0)');
        localStorage.setItem("theme-sell", "rgb(219, 0, 0)");
        localStorage.setItem("theme-buy", "rgb(0, 189, 0)");
        closeChangeTheme();
    }
    else if (theme == 4) {
        root.style.setProperty('--sell', '#f23645');
        root.style.setProperty('--buy', '#089981');
        localStorage.setItem("theme-sell", "#f23645");
        localStorage.setItem("theme-buy", "#089981");
        closeChangeTheme();
    }
    else if (theme == 5) {
        root.style.setProperty('--sell', 'rgb(220, 20, 90)');
        root.style.setProperty('--buy', 'rgb(0, 136, 148)');
        localStorage.setItem("theme-sell", "rgb(220, 20, 90)");
        localStorage.setItem("theme-buy", "rgb(0, 136, 148)");
        closeChangeTheme();
    }
}
if (localStorage.getItem('theme-sell') != null) {
    root.style.setProperty('--sell', localStorage.getItem('theme-sell'));
}
if (localStorage.getItem('theme-buy') != null) {
    root.style.setProperty('--buy', localStorage.getItem('theme-buy'));
}

if (localStorage.getItem('exchange-pop') == null) {
    openExchangePop();
}


// checking for any URL mode

let mode = document.getElementById("mode").innerHTML;
if (mode === 'control') {
    document.getElementById('control-wrapper').style.display = 'flex';
}


// Token searching logic here
let all_tokens;
async function retrive() {
    all_tokens = await returnAllTokens();
    all_tokens = JSON.parse(all_tokens)
}
$(document).ready(async function () {
    await new Promise(r => setTimeout(r, 2000));
    retrive();
});

function searchToken() {
    foundTokens = [];
    found_counter = 0;
    let query = document.getElementById('change-token-input').value;
    query = query.toLowerCase();
    if (query.length > 0 && all_tokens != undefined) {
        for (var i = 0; i < all_tokens.length; i++) {
            let name = (all_tokens[i].fields.name).toLowerCase();
            let symbol = (all_tokens[i].fields.symbol).toLowerCase();
            let address = (all_tokens[i].fields.address).toLowerCase();
            if (name.includes(query) || symbol.includes(query) || address.includes(query)) {
                foundTokens.push(all_tokens[i]);
                found_counter += 1;
            }
        }
        if (found_counter == 0) {
            document.getElementById('not-found').style.display = 'flex';
        }
    }
    else {
        document.getElementById('not-found').style.display = 'none';
        foundTokens = all_tokens;
    }
    var html_list = "";
    for (var i = 0; i < foundTokens.length; i++) {
        html_list += `<a href="/exchange/${chainSlug}/${foundTokens[i].fields.address}/${foundTokens[i].fields.url_slug}">
        <div class="availableTokenItem">`
        if (foundTokens[i].fields.icon == "" || foundTokens[i].fields.icon == null) {
            html_list += `<img src="${defaultIconURL}" alt="token-icon">`
        }
        else {
            html_list += `<img src="${foundTokens[i].fields.icon_url}" alt="token-icon">`
        }
        html_list += `<p>${foundTokens[i].fields.symbol} / USD</p>
            <p>${foundTokens[i].fields.name}</p>
        </div>
    </a>`
    }
    $("#available-token-list").html(html_list);
}


async function redirectSwap() {
    query = document.getElementById('change-token-input').value;
    location.href = `https://swap.haloxchange.com/?search=${query}`;
}