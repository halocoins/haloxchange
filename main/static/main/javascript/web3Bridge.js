let web3;
let userAddress;
let tokenBalance = 0;
let tokenWeiBalance = 0;
let currencyBalance = 0;
let currency = 'BNB';
let minBuySell = 10;
let maxBuySell = 1000000000000;

let tradeMode = 'limit';
let orderMode = 'book';
let historyMode = 'current';

let token_address = document.getElementById('token-address').innerHTML;
let url_slug = document.getElementById('token-slug').innerHTML;
let decimals_ = document.getElementById('token-decimals').innerHTML;

let chain = document.getElementById('chain').innerHTML;

let networkName = blockchainData[chain].networkName;
let chainId = blockchainData[chain].chainId;
let chainSlug = blockchainData[chain].chainSlug;
let symbol = blockchainData[chain].symbol;
let contractAddress = blockchainData[chain].smartContract;
let logoURL = blockchainData[chain].logoURL;
let apiKey = blockchainData[chain].apiKey;
let gasLimit = blockchainData[chain].gasLimit;
let gasLimitTrans = blockchainData[chain].gasLimitTrans;
let gasTracker = blockchainData[chain].gasTracker;
let importURL = blockchainData[chain].importURL;
let defaultIconURL = blockchainData[chain].defaultIconURL;
let defaultToken = blockchainData[chain].defaultToken
let defaultTokenURL = blockchainData[chain].defaultTokenURL
let defaultTokenSymbol = blockchainData[chain].defaultTokenSymbol;
let tokenList = blockchainData[chain].tokenList;

changeNetwork(chain, false);

async function web3App(wallet, injected) {
    web3 = await getWeb3(wallet, injected);
    currentChain = await web3.eth.getChainId();
    currentChain = parseInt(currentChain.toString())
    if (currentChain === chainId) {
        const accounts = await web3.eth.getAccounts();
        console.log("Account Connected:", accounts);
        userAddress = accounts[0];

        currencyBalance = await web3.eth.getBalance(userAddress);
        currencyBalance = web3.utils.fromWei(currencyBalance, 'ether')
        document.getElementById('currency-balance').innerHTML = Number(currencyBalance).toFixed(4);

        const tokenContract = await getTokenContract(web3, token_address);
        tokenBalance = await tokenContract.methods.balanceOf(userAddress).call({ from: userAddress });
        tokenWeiBalance = tokenBalance;
        tokenBalance = tokenBalance / 10 ** Number(decimals_);
        document.getElementById('token-balance').innerHTML = Number(tokenBalance).toFixed(4);

        let button = document.getElementById('connect-wallet-btn');
        button.innerHTML = truncateEthAddress(userAddress);
        button.style.background = 'transparent';
        button.style.color = 'orange';
    }
    else {
        forceNetworkSwitch(chainId);
        openGlobalError('Wrong Network Detected, change and retry', 8000);
    }
}

async function updateBalances() {
    if (userAddress) {
        currencyBalance = await web3.eth.getBalance(userAddress);
        currencyBalance = web3.utils.fromWei(currencyBalance)
        document.getElementById('currency-balance').innerHTML = Number(currencyBalance).toFixed(4);

        const tokenContract = await getTokenContract(web3, token_address);
        tokenBalance = await tokenContract.methods.balanceOf(userAddress).call({ from: userAddress });
        tokenWeiBalance = tokenBalance;
        let decimals = await tokenContract.methods.decimals().call()
        tokenBalance = tokenBalance / 10 ** decimals;
        document.getElementById('token-balance').innerHTML = Number(tokenBalance).toFixed(4);
    }
}

async function checkClaimReward() {
    let contract = await getContract(web3);
    let number = await getNumberOfListedTokens(userAddress);
    let rewardAmount = await contract.methods.tokenListers(userAddress).call();
    document.getElementById('claim-listed-tokens').innerHTML = number;
    document.getElementById('claim-listed-reward').innerHTML = web3.utils.fromWei(rewardAmount);
    openClaimReward();
}

async function claimReward() {
    let contract = await getContract(web3);
    contract.methods.claimReward().send({ from: userAddress })
        .on('transaction', function (hash) {
            console.log("Transaction: ", hash);
        })
        .on('confirmation', function (confirmationNumber, receipt) {
            if (confirmationNumber == 6) {
                console.log(receipt);
            }
        })
        .on('receipt', function (receipt) {
            console.log('receipt:', receipt);
            closeClaimReward();
            openGlobalInfo("Reward Claimed", 4000)
        })
        .on('error', function (error, receipt) {
            console.log('Error:', error);
            console.log('Error:', receipt);
        })
}

async function validateTokenListing() {
    document.getElementById('token-list-error').innerHTML = "";
    document.getElementById('token-list-error').style.display = 'none';
    document.getElementById('list-token-details').style.display = 'none';
    document.getElementById('list-token-btn').disabled = true;

    let address = document.getElementById('token-list-address').value;
    if (address) {
        if (web3.utils.isAddress(address)) {
            try {
                let tokenContract = await getTokenContract(web3, address);
                let decimals = await tokenContract.methods.decimals().call();
                let name = await tokenContract.methods.name().call();
                let symbol = await tokenContract.methods.symbol().call()
                document.getElementById('list-token-details').style.display = 'flex';
                document.getElementById('list-token-name').innerHTML = name;
                document.getElementById('list-token-symbol').innerHTML = symbol;
                document.getElementById('list-token-decimals').innerHTML = decimals;
                document.getElementById('list-token-btn').disabled = false;
            }
            catch (error) {
                console.log(error);
                document.getElementById('token-list-error').innerHTML = "Not a valid Token";
                document.getElementById('token-list-error').style.display = 'block';
                document.getElementById('list-token-details').style.display = 'none';
                document.getElementById('list-token-btn').disabled = true;
            }
        }
        else {
            document.getElementById('token-list-error').innerHTML = "Not a valid address";
            document.getElementById('token-list-error').style.display = 'block';
            document.getElementById('list-token-details').style.display = 'none';
            document.getElementById('list-token-btn').disabled = true;
        }
    }
}

async function listToken() {
    console.log("Clicked")
    openListingLoader();
    let contract = await getContract(web3);
    let address = document.getElementById('token-list-address').value;

    let fetchedGasPrice = await getSafeGasPrice();

    if (fetchedGasPrice) {
        contract.methods.listToken(address).send({ from: userAddress, gas: gasLimit, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
            .on('transaction', function (hash) {
                console.log("Transaction: ", hash);
            })
            .on('confirmation', function (confirmationNumber, receipt) {
                if (confirmationNumber == 6) {
                    console.log(receipt);
                }
            })
            .on('receipt', async function (receipt) {
                console.log('receipt:', receipt);
                let name = document.getElementById('list-token-name').innerHTML;
                let symbol = document.getElementById('list-token-symbol').innerHTML;
                let decimals = document.getElementById('list-token-decimals').innerHTML;

                data = await fetchCoinGecko();
                let icon_url = '';

                for (var i = 0; i < data.length; i++) {
                    if (data[i].name.toLowerCase() === name.toLowerCase() && data[i].symbol.toLowerCase() === symbol.toLowerCase()) {
                        icon_url = data[i].logoURI;
                        break;
                    }
                }

                saveListToken(address, name, symbol, decimals, icon_url);
                closeListingLoader();

            })
            .on('error', function (error, receipt) {
                console.log('Error:', error);
                console.log('Error:', receipt);
                closeListingLoader();
            })
    }
    else {
        closeListingLoader();
        openGlobalError("Something went wrong, please try after some time", 10000);
    }

}

async function saveListToken(tokenAddress, name, symbol, decimals, icon_url) {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: `/${chainSlug}/list_token/`,
        type: 'POST',
        data: {
            'address': tokenAddress,
            'name': name,
            'symbol': symbol,
            'decimals': decimals,
            'user': userAddress,
            'icon_url': icon_url,
        },
        headers: { 'X-CSRFToken': csrfToken },
        success: function (response) {
            console.log(response);
            closeListToken();
            openGlobalInfo(
                "Token Listed Successfully!<br>Now place one Sell and one Buy order for Token",
                10000
            )
            location.reload();
        },
        error: function (xhr, status, error) {
            console.error(xhr.responseText);
        }
    })
}

async function validateBuyPrice() {
    validateBuyAmount();
    let price = document.getElementById('buy-price-input').value;
    if (price) {
        price = Number(price)
        let bnbPrice = await getBNBPrice()
        let msg = "≈ " + (price / bnbPrice) + " " + symbol;
        // displayBuyConversion(msg, 5000);
    }
}

async function validateSellPrice() {
    validateSellAmount();
    let price = document.getElementById('sell-price-input').value;
    if (price) {
        price = Number(price)
        let bnbPrice = await getBNBPrice()
        let msg = "≈ " + (price / bnbPrice) + " " + symbol;
        // displaySellConversion(msg, 5000);
    }
}

async function validateBuyAmount() {
    closeBuyError();
    document.getElementById('total-buy-amount').innerHTML = '0.0000';
    document.getElementById('total-buy-usd').innerHTML = '0.00';
    let amount = document.getElementById('buy-amount-input').value;
    if (amount) {
        if (amount < minBuySell) {
            openBuyError("Minimum Buy amount is " + minBuySell);
        }
        else if (amount >= minBuySell) {
            let price = document.getElementById('buy-price-input').value;
            let bnbPrice = await getBNBPrice();
            let total = (price / bnbPrice) * amount;
            document.getElementById('total-buy-amount').innerHTML = Number(total).toFixed(4)
            let total_usd = amount * price;
            document.getElementById('total-buy-usd').innerHTML = Number(total_usd).toFixed(2)
        }
        else {
            openBuyError("Maximum Buy amount is " + maxBuySell);
        }
    }
}

async function validateSellAmount() {
    closeSellError();
    document.getElementById('total-sell-amount').innerHTML = '0.0000';
    document.getElementById('total-sell-usd').innerHTML = '0.00';
    let amount = document.getElementById('sell-amount-input').value;
    if (amount) {
        if (amount < minBuySell) {
            openSellError("Minimum Sell amount is " + minBuySell);
        }
        else if (amount >= minBuySell) {
            let price = document.getElementById('sell-price-input').value;
            let bnbPrice = await getBNBPrice();
            let total = (price / bnbPrice) * amount;
            document.getElementById('total-sell-amount').innerHTML = Number(total).toFixed(4)
            let total_usd = amount * price;
            document.getElementById('total-sell-usd').innerHTML = Number(total_usd).toFixed(2)
        }
        else {
            openSellError("Maximum Sell amount is " + maxBuySell);
        }
    }
}

async function placeBuyOrder() {
    if (userAddress) {
        let price = document.getElementById('buy-price-input').value;
        let amount = document.getElementById('buy-amount-input').value;

        if (tradeMode == 'market') {
            price = document.getElementById('current-price').innerHTML;
        }

        if (price.length != 0 && amount.length != 0 && amount >= minBuySell) {
            let captured_price = await getBNBPrice();
            if (captured_price === 0) {
                openGlobalError("SOMETHING WENT WRONG : TRY DISABLING YOUR ADBLOCKER");
            }
            let total = (amount * price) / captured_price;
            let toExchange = (0.075 * total) / 100;
            total += toExchange;
            if (total >= currencyBalance) {
                openGlobalError("Insufficient Balance", 3000);
            }
            else {
                const tokenContract = await getTokenContract(web3, token_address);
                let decimals = await tokenContract.methods.decimals().call()


                captured_price = web3.utils.toWei(captured_price.toString(), 'ether')
                captured_price = web3.utils.toBN(captured_price)

                price = web3.utils.toWei(price.toString(), 'ether')
                price = web3.utils.BN(price);

                total = total.toFixed(8).toString()
                total = web3.utils.toWei(total, 'ether');

                let amount_wei = web3.utils.toWei(amount.toString(), 'ether')
                amount_wei = web3.utils.toBN(amount_wei).div(web3.utils.toBN(10 ** (18 - decimals)));


                let order_id = await newOrderID();
                let orders = await checkSellOrders(token_address, price)

                if (tradeMode == 'market' && orders.length == 0) {
                    openGlobalError("No order available to fulfill", 4000)
                }
                else {

                    console.log(amount_wei.toString())
                    console.log(token_address.toString())
                    console.log(captured_price.toString())
                    console.log(price.toString())
                    console.log(order_id.toString())
                    console.log(orders)
                    console.log("Total:", total)

                    let fetchedGasPrice = await getSafeGasPrice();

                    if (fetchedGasPrice) {
                        let contract = await getContract(web3);
                        contract.methods.placeBuyOrder(order_id, token_address, captured_price, price, amount_wei, orders).send({ value: total, from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
                            .on('transaction', function (hash) {
                                console.log("Transaction: ", hash);
                            })
                            .on('receipt', function (receipt) {
                                console.log('receipt:', receipt);
                                amount_wei = amount_wei.toString()
                                captured_price = captured_price.toString()
                                price = price.toString()
                                saveBuyOrder(order_id, token_address, captured_price, amount_wei, price)
                            })
                            .on('error', function (error, receipt) {
                                console.log('Error:', error);
                                console.log('Error:', receipt);
                            })
                    }
                    else {
                        openGlobalError("Something went wrong, please try after some time", 10000);
                    }
                }

            }
        }
    }
}

async function placeSellOrder() {
    if (userAddress) {
        let price = document.getElementById('sell-price-input').value;
        let amount = document.getElementById('sell-amount-input').value;

        if (tradeMode == 'market') {
            price = await getMaxBuyPrice(token_address)
            price = price.toString()
            console.log(price)
        }

        if (price == -1) {
            openGlobalError("No order available to fulfill", 4000)
        }

        if (price.length != 0 && amount.length != 0 && amount >= minBuySell && price != -1) {
            const tokenContract = await getTokenContract(web3, token_address);
            let decimals = await tokenContract.methods.decimals().call()

            let captured_price = await getBNBPrice();
            if (captured_price === 0) {
                openGlobalError("SOMETHING WENT WRONG : TRY DISABLING YOUR ADBLOCKER");
            }
            if (amount > tokenBalance) {
                openGlobalError("Insufficient Balance", 3000);
            }
            else {
                const tokenContract = await getTokenContract(web3, token_address);

                captured_price = web3.utils.toWei(captured_price.toString(), 'ether')
                captured_price = web3.utils.toBN(captured_price)
                if (tradeMode != 'market') {
                    price = web3.utils.toWei(price.toString(), 'ether')
                }
                price = web3.utils.BN(price);

                let amount_wei = web3.utils.toWei(amount.toString(), 'ether')
                amount_wei = web3.utils.toBN(amount_wei).div(web3.utils.toBN(10 ** (18 - decimals)));


                let order_id = await newOrderID();
                let orders = await checkBuyOrders(token_address, price)

                console.log(amount_wei.toString())
                console.log(token_address.toString())
                console.log(captured_price.toString())
                console.log(price.toString())
                console.log(order_id.toString())
                console.log(orders)

                let fetchedGasPrice = await getSafeGasPrice();

                if (fetchedGasPrice) {

                    let allowance = await tokenContract.methods.allowance(userAddress, contractAddress).call();
                    console.log("Allowance:", allowance);
                    if (Number(allowance) < Number(amount_wei)) {
                        await tokenContract.methods.approve(contractAddress, tokenWeiBalance).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
                            .then(function (receipt) {
                                console.log("Approved!: ", receipt);
                            })
                    }

                    let contract = await getContract(web3);
                    contract.methods.placeSellOrder(order_id, token_address, captured_price, price, amount_wei, orders).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
                        .on('transaction', function (hash) {
                            console.log("Transaction: ", hash);
                        })
                        .on('receipt', function (receipt) {
                            console.log('receipt:', receipt);
                            amount_wei = amount_wei.toString()
                            captured_price = captured_price.toString()
                            price = price.toString()
                            saveSellOrder(order_id, token_address, captured_price, amount_wei, price)
                        })
                        .on('error', function (error, receipt) {
                            console.log('Error:', error);
                            console.log('Error:', receipt);
                        })
                }
                else {
                    openGlobalError("Something went wrong, please try after some time", 10000);
                }
            }
        }
    }
}


async function saveBuyOrder(order_id, token, captured_price, amount, price) {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: `/exchange/${chainSlug}/place_buy_order/`,
        type: 'POST',
        data: {
            'order_id': order_id,
            'token': token,
            'captured_price': captured_price,
            'amount': amount,
            'price': price,
            'user': userAddress
        },
        headers: { 'X-CSRFToken': csrfToken },
        success: function (response) {
            console.log(response);
            openGlobalInfo(
                "Order Placed",
                2000
            )
        },
        error: function (xhr, status, error) {
            console.error(xhr.responseText);
        }
    })
}


async function saveSellOrder(order_id, token, captured_price, amount, price) {
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        url: `/exchange/${chainSlug}/place_sell_order/`,
        type: 'POST',
        data: {
            'order_id': order_id,
            'token': token,
            'captured_price': captured_price,
            'amount': amount,
            'price': price,
            'user': userAddress
        },
        headers: { 'X-CSRFToken': csrfToken },
        success: function (response) {
            console.log(response);
            openGlobalInfo(
                "Order Placed",
                2000
            )
        },
        error: function (xhr, status, error) {
            console.error(xhr.responseText);
        }
    })
}

async function revokeSellOrder(order_id) {
    let contract = await getContract(web3);
    let fetchedGasPrice = await getSafeGasPrice();

    contract.methods.revokeSellOrder(order_id).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
        .on('transaction', function (hash) {
            console.log("Transaction: ", hash);
        })
        .on('receipt', function (receipt) {
            console.log('receipt:', receipt);
            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: `/exchange/${chainSlug}/revoke_sell_order`,
                type: 'POST',
                data: {
                    'order_id': order_id,
                },
                headers: { 'X-CSRFToken': csrfToken },
                success: function (response) {
                    console.log(response);
                    openGlobalError(
                        "Order Revoked",
                        2000
                    )
                },
                error: function (xhr, status, error) {
                    console.error(xhr.responseText);
                }
            })
        })
        .on('error', function (error, receipt) {
            console.log('Error:', error);
            console.log('Error:', receipt);
        })
}

async function revokeBuyOrder(order_id) {
    let contract = await getContract(web3);
    let fetchedGasPrice = await getSafeGasPrice();

    contract.methods.revokeBuyOrder(order_id).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
        .on('transaction', function (hash) {
            console.log("Transaction: ", hash);
        })
        .on('receipt', function (receipt) {
            console.log('receipt:', receipt);
            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: `/exchange/${chainSlug}/revoke_buy_order`,
                type: 'POST',
                data: {
                    'order_id': order_id,
                },
                headers: { 'X-CSRFToken': csrfToken },
                success: function (response) {
                    console.log(response);
                    openGlobalError(
                        "Order Revoked",
                        2000
                    )
                },
                error: function (xhr, status, error) {
                    console.error(xhr.responseText);
                }
            })
        })
        .on('error', function (error, receipt) {
            console.log('Error:', error);
            console.log('Error:', receipt);
        })
}


// control-center-functions-------
async function dListToken() {
    let tokenAddress = document.getElementById("dlist-token-input").value;
    let recipientAddress = document.getElementById("dlist-recipient-input").value;
    if (tokenAddress.length != 0 && recipientAddress.length != 0) {
        let contract = await getContract(web3);
        let fetchedGasPrice = await getSafeGasPrice();


        contract.methods.dlistToken(tokenAddress, recipientAddress).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
            .on('transaction', function (hash) {
                console.log("Transaction: ", hash);
            })
            .on('receipt', function (receipt) {
                console.log('receipt:', receipt);
                alert("Token Dlisted");
            })
            .on('error', function (error, receipt) {
                console.log('Error:', error);
                console.log('Error:', receipt);
            })

    }
}

async function collectFee() {
    let recipientAddress = document.getElementById("fee-collect-recipent").value;
    if (recipientAddress.length != 0) {
        let contract = await getContract(web3);
        let fetchedGasPrice = await getSafeGasPrice();

        contract.methods.collectFee(recipientAddress).send({ from: userAddress, gas: gasLimitTrans, gasPrice: web3.utils.toWei(fetchedGasPrice, 'gwei') })
            .on('transaction', function (hash) {
                console.log("Transaction: ", hash);
            })
            .on('receipt', function (receipt) {
                console.log('receipt:', receipt);
                alert("Fee Collected");
            })
            .on('error', function (error, receipt) {
                console.log('Error:', error);
                console.log('Error:', receipt);
            })

    }
}
// control-center-functions-------ends




async function getSafeGasPrice() {
    try {
        const response = await fetch(gasTracker + apiKey);
        const data = await response.json();
        let safeGasPrice = data.result.ProposeGasPrice;

        if (chainId === 137) { // polygon
            safeGasPrice = data.result.FastGasPrice;
            safeGasPrice = (Number(safeGasPrice) + 25).toString();
        }
        else if (chainId === 56) { // BSC
            safeGasPrice = data.result.ProposeGasPrice;
        }
        return safeGasPrice;
    } catch (error) {
        console.error('Error:', error);
        return null; // or you can throw an error
    }
}

// update chain data on-change -----------------
async function updateChainData() {
    networkName = blockchainData[chain].networkName;
    chainId = blockchainData[chain].chainId;
    chainSlug = blockchainData[chain].chainSlug;
    symbol = blockchainData[chain].symbol;
    contractAddress = blockchainData[chain].smartContract;
    logoURL = blockchainData[chain].logoURL;
    apiKey = blockchainData[chain].apiKey;
    gasLimit = blockchainData[chain].gasLimit;
    gasTracker = blockchainData[chain].gasTracker;
    importURL = blockchainData[chain].importURL;
    defaultIconURL = blockchainData[chain].defaultIconURL;
    tokenList = blockchainData[chain].tokenList;
}


// auto-connect-wallet -----------------starts
let providerStorage = localStorage.getItem('walletProvider');
console.log(providerStorage)
if (providerStorage != null) {
    if (providerStorage != 'walletconnect') {
        web3App(providerStorage, true);
    }
    else {
        web3App(providerStorage, false);
    }
}

async function disconnectWallet() {
    closeWalletDis();
    localStorage.removeItem('walletProvider');
    await new Promise(r => setTimeout(r, 500));
    location.reload();
}
// auto-connect-wallet -------------------ends



// auto-change-newtork--------
function autoNetworkSwitch() {
    const networkStorage = localStorage.getItem('network')
    if (networkStorage) {
        changeNetwork(networkStorage, false);
    }
}

autoNetworkSwitch();