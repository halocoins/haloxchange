// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title BEP20
 * @dev Interface for the BEP20 standard token.
 */
interface BEP20 {
    function name() external view returns (string memory);

    function symbol() external view returns (string memory);

    function totalSupply() external view returns (uint256);

    function decimals() external view returns (uint8);

    function balanceOf(address account) external view returns (uint256);

    function transfer(address recipient, uint256 amount)
        external
        returns (bool);

    function allowance(address owner, address spender)
        external
        view
        returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(
        address indexed owner,
        address indexed spender,
        uint256 value
    );
}

/**
 * @title ExchangeEngine
 * @dev This contract implements a decentralized exchange engine.
 */
contract ExchangeEngine {
    address public admin;
    address public dlister;
    address public feeCollector;

    uint256 public collectedFeeAmount_ = 0;
    uint256 public exchangeFee_; // * 100, (0.07% = 7)

    struct ListedToken {
        address tokenAddress;
        string tokenName;
        string tokenSymbol;
        uint8 decimals;
        address listedBy;
        uint256 listedOn;
        bool dlisted;
    }

    struct BuyOrder {
        address token;
        uint256 captured_price;
        uint256 price;
        uint256 amount;
        address user;
        uint256 completed;
        uint256 timestamp;
        bool executed;
        bool can_revoke;
        bool revoked;
    }
    struct SellOrder {
        address token;
        uint256 captured_price;
        uint256 price;
        uint256 amount;
        address user;
        uint256 completed;
        uint256 timestamp;
        bool executed;
        bool can_revoke;
        bool revoked;
    }

    ListedToken[] public listedTokensList;

    mapping(string => address) public urlToToken;
    mapping(address => string) public tokenToUrl;
    mapping(address => ListedToken) public listedTokens;
    mapping(string => BuyOrder) public buyOrders;
    mapping(string => SellOrder) public sellOrders;
    mapping(address => uint256) public tokenListers;

    /**
     * @dev Modifier to check if the caller is the admin.
     */
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can call this function.");
        _;
    }

    /**
     * @dev Modifier to check if the caller is the dlister.
     */
    modifier onlyDlister() {
        require(msg.sender == dlister, "Only dlister can call this function.");
        _;
    }

    /**
     * @dev Modifier to check if the caller is the fee collector.
     */
    modifier onlyFeeCollector() {
        require(
            msg.sender == feeCollector,
            "Only feeCollector can call this function."
        );
        _;
    }

    /**
     * @dev Constructor function.
     * @param dlister_ The address of the dlister.
     * @param feeCollector_ The address of the fee collector.
     * @param exchangeFee The exchange fee percentage.
     */
    constructor(address dlister_, address feeCollector_, uint256 exchangeFee) {
        admin = msg.sender;
        dlister = dlister_;
        feeCollector = feeCollector_;
        exchangeFee_ = exchangeFee;
    }

    /**
     * @dev Places a buy order.
     * @param order_id The ID of the order.
     * @param token The address of the token.
     * @param captured_price The captured price of the token.
     * @param price The price of the token.
     * @param amount The amount of the token.
     * @param to_execute The list of orders to execute.
     */
    function placeBuyOrder (
        string calldata order_id,
        address token,
        uint256 captured_price,
        uint256 price,
        uint256 amount,
        string[] calldata to_execute
    ) public payable {
        uint256 token_decimals = listedTokens[token].decimals;
        require(!listedTokens[token].dlisted, "Token is not valid");
        require(!orderIDExist(order_id), "order_id not unique");
        require(tokenListed(token), "Token not listed");

        uint256 amount_to_deduct = (amount * price) / captured_price;
        amount_to_deduct = amount_to_deduct * 10 ** (18 - token_decimals);
        require(msg.value >= amount_to_deduct, "Transferred amount is less");

        uint256 toExchange = (exchangeFee_ * amount_to_deduct) / 10000; // dividing with 100 for actual %
        collectedFeeAmount_ += toExchange;

        BuyOrder memory order;
        order.token = token;
        order.captured_price = captured_price;
        order.price = price; 
        order.amount = amount;
        order.user = msg.sender;
        order.timestamp = block.timestamp;
        order.can_revoke = true;
        order.revoked = false;

        if (to_execute.length == 0) {
            order.executed = false;
        } else {
            uint256 amount_to_buy = amount;
            for (uint32 i = 0; i < to_execute.length; i++) {
                string memory id_ = to_execute[i];
                if (
                    sellOrders[id_].price <= price && 
                    !sellOrders[id_].executed &&
                    sellOrders[id_].completed < sellOrders[id_].amount &&
                    amount_to_buy > 0 && !sellOrders[id_].revoked
                ) {
                    uint256 amount_check = sellOrders[id_].amount - sellOrders[id_].completed;
                    if (amount_to_buy >= amount_check) {
                        amount_to_buy -= amount_check;
                        BEP20(token).transfer(msg.sender, amount_check);

                        sellOrders[id_].completed = sellOrders[id_].amount;
                        sellOrders[id_].executed = true;
                        sellOrders[id_].can_revoke = false;

                        uint256 value_to_transfer = ((amount_check * sellOrders[id_].price) / sellOrders[id_].captured_price);
                        toExchange = (exchangeFee_ * value_to_transfer) / 10000;
                        
                        value_to_transfer = value_to_transfer * 10 ** (18 - token_decimals);
                        toExchange = toExchange * 10 ** (18 - token_decimals);

                        value_to_transfer = value_to_transfer - toExchange;
                        collectedFeeAmount_ += toExchange;

                        _safeTransferBNB(address(sellOrders[id_].user), value_to_transfer);
                        order.completed += amount_check;

                    } else if (amount_to_buy < amount_check) {
                        BEP20(token).transfer(msg.sender, amount_to_buy);

                        sellOrders[id_].completed += amount_to_buy;

                        uint256 value_to_transfer = (amount_to_buy * sellOrders[id_].price) / sellOrders[id_].captured_price;
                        toExchange = (exchangeFee_ * value_to_transfer) / 10000;
                        
                        value_to_transfer = value_to_transfer * 10 ** (18 - token_decimals);
                        toExchange = toExchange * 10 ** (18 - token_decimals);

                        value_to_transfer = value_to_transfer - toExchange;
                        collectedFeeAmount_ += toExchange;

                        _safeTransferBNB(address(sellOrders[id_].user), value_to_transfer);

                        amount_to_buy = 0;
                        order.completed = amount;
                        order.executed = true;
                        order.can_revoke = false;
                    }
                }

                if (amount_to_buy <= 0) {
                    break;
                }
                
            }
        }
        if (order.completed == order.amount) {
            order.executed = true;
            order.can_revoke = false;
        }
        buyOrders[order_id] = order;
    }

    /**
     * @dev Places a sell order.
     * @param order_id The ID of the order.
     * @param token The address of the token.
     * @param captured_price The captured price of the token.
     * @param price The price of the token.
     * @param amount The amount of the token.
     * @param to_execute The list of orders to execute.
     */
    function placeSellOrder(
        string calldata order_id,
        address token,
        uint256 captured_price,
        uint256 price,
        uint256 amount,
        string[] calldata to_execute
    ) public {
        uint256 token_decimals = listedTokens[token].decimals;
        require(!listedTokens[token].dlisted, "Token is not valid");
        require(!orderIDExist(order_id), "order_id not unique");
        require(tokenListed(token), "Token not listed");

        uint256 amount_to_deduct = amount;
        BEP20(token).transferFrom(msg.sender, address(this), amount_to_deduct);

        uint256 toExchange;

        SellOrder memory order;
        order.token = token;
        order.captured_price = captured_price;
        order.price = price;
        order.amount = amount;
        order.user = msg.sender;
        order.timestamp = block.timestamp;
        order.can_revoke = true;
        order.revoked = false;


        if (to_execute.length == 0) {
            order.completed = 0;
            order.executed = false;
        } else {
            uint256 amount_to_sell = amount;
            for (uint256 i = 0; i < to_execute.length; i++) {
                string calldata id_ = to_execute[i];
                if (
                    buyOrders[id_].price >= price &&
                    !buyOrders[id_].executed &&
                    buyOrders[id_].completed < buyOrders[id_].amount &&
                    amount_to_sell > 0 && !buyOrders[id_].revoked
                ) {
                    uint256 amount_check = buyOrders[id_].amount - buyOrders[id_].completed;
                    if (amount_to_sell >= amount_check) {
                        amount_to_sell -= amount_check;
                        BEP20(token).transfer(buyOrders[id_].user, amount_check);

                        buyOrders[id_].completed = buyOrders[id_].amount;
                        buyOrders[id_].executed = true;
                        buyOrders[id_].can_revoke = false;

                        uint256 value_to_transfer = (amount_check * buyOrders[id_].price) / buyOrders[id_].captured_price;
                        toExchange = (exchangeFee_ * value_to_transfer) / 10000;

                        value_to_transfer = value_to_transfer * 10 ** (18 - token_decimals);
                        toExchange = toExchange * 10 ** (18 - token_decimals);

                        value_to_transfer = value_to_transfer - toExchange;

                        _safeTransferBNB(address(msg.sender), value_to_transfer);
                        order.completed += amount_check;

                    } else if (amount_to_sell < amount_check) {
                        BEP20(token).transfer(buyOrders[id_].user, amount_to_sell);

                        buyOrders[id_].completed += amount_to_sell;

                        uint256 value_to_transfer = (amount_to_sell * buyOrders[id_].price) / buyOrders[id_].captured_price;
                        toExchange = (exchangeFee_ * value_to_transfer) / 10000;

                        value_to_transfer = value_to_transfer * 10 ** (18 - token_decimals);
                        toExchange = toExchange * 10 ** (18 - token_decimals);

                        value_to_transfer = value_to_transfer - toExchange;

                        _safeTransferBNB(address(msg.sender), value_to_transfer);

                        amount_to_sell = 0;
                        order.completed = amount;
                        order.executed = true;
                        order.can_revoke = false;
                    }
                }

                if (amount_to_sell <= 0) {
                    break;
                }
            }
        }
        if (order.completed == order.amount) {
            order.executed = true;
            order.can_revoke = false;
        }

        sellOrders[order_id] = order;
    }

    /**
     * @dev Revoke a sell order or a buy order.
     * @param order_id The ID of the order to be revoked.
     */
    function revokeSellOrder(string memory order_id) public {
        require(orderIDExist(order_id));
        require(sellOrders[order_id].user == msg.sender);
        require(sellOrders[order_id].can_revoke && !sellOrders[order_id].revoked);
        sellOrders[order_id].revoked = true;
        address token = sellOrders[order_id].token;
        uint256 amount = sellOrders[order_id].amount - sellOrders[order_id].completed;
        BEP20(token).transfer(msg.sender, amount);
    } 

    function revokeBuyOrder(string memory order_id) public {
        require(orderIDExist(order_id));
        require(buyOrders[order_id].user == msg.sender);
        require(buyOrders[order_id].can_revoke && !buyOrders[order_id].revoked);
        uint256 token_decimals = listedTokens[buyOrders[order_id].token].decimals;
        buyOrders[order_id].revoked = true;
        uint256 amount = (buyOrders[order_id].amount - buyOrders[order_id].completed) * (buyOrders[order_id].price) / (buyOrders[order_id].captured_price);
        uint256 toExchange = (exchangeFee_ * amount) / 10000;

        amount = amount * 10 ** (18 - token_decimals);
        toExchange = toExchange * 10 ** (18 - token_decimals);
        collectedFeeAmount_ -= toExchange;

        _safeTransferBNB(address(msg.sender), amount);
    }

    function orderIDExist(string memory order_id) public view returns (bool) {
        bool exist = false;
        if (buyOrders[order_id].price != 0) {
            exist = true;
        }
        if (sellOrders[order_id].price != 0) {
            exist = true;
        }
        return exist;
    }

    function tokenListed(address _tokenAddress) public view returns (bool) {
        ListedToken memory structValue = listedTokens[_tokenAddress];
        bool listed = false;
        if (structValue.tokenAddress != address(0)) {
            if(structValue.dlisted == true) {
                listed = false;
            }
            else {
                listed = true;
            }
        }
        return listed;
    }

    function listToken(address _tokenAddress) public {
        require(!tokenListed(_tokenAddress), "Token already listed!");
        BEP20 Token = BEP20(_tokenAddress);

        ListedToken memory token;
        token.tokenAddress = _tokenAddress;
        token.tokenName = Token.name();
        token.tokenSymbol = Token.symbol();
        token.decimals = Token.decimals();
        token.listedBy = msg.sender;
        token.listedOn = block.timestamp;
        token.dlisted = false;

        string memory pair_slug = string.concat(Token.symbol(), "_USD");
        urlToToken[pair_slug] = _tokenAddress;
        tokenToUrl[_tokenAddress] = pair_slug;

        listedTokens[_tokenAddress] = token;
        listedTokensList.push(token);
    }

    function _safeTransferBNB(address to, uint256 value) internal {
        (bool success, ) = to.call{value: value}("");
        require(success, "TransferHelper: BNB_TRANSFER_FAILED");
    }

    function allListedTokens() external view returns (ListedToken[] memory) {
        return listedTokensList;
    }

    function collectBNB(address recepient) external onlyAdmin {
        uint256 amount = address(this).balance;
        _safeTransferBNB(address(recepient), amount);
    }

    function collectFee(address recipient) external onlyFeeCollector {
        _safeTransferBNB(address(recipient), collectedFeeAmount_);
        collectedFeeAmount_ = 0;
    }

    function collectToken(address token, address recepient) external onlyAdmin {
        BEP20 Token = BEP20(token);
        uint256 balance_ = Token.balanceOf(address(this));
        Token.transfer(recepient, balance_);
    }

    function changeStandards(
        uint256 newExchangeFee
    ) public onlyAdmin {
        exchangeFee_ = newExchangeFee;
    }

    function changeOwners(
        address newAdmin,
        address newDlister,
        address newFeeCollector
    ) public onlyAdmin {
        admin = newAdmin;
        dlister = newDlister;
        feeCollector = newFeeCollector;
    }

    function dlistToken(address token, address recipient) public onlyDlister {
        listedTokens[token].dlisted = true;
        BEP20 Token = BEP20(token);
        uint256 balance_ = Token.balanceOf(address(this));
        Token.transfer(recipient, balance_);
    }


    receive() payable external {

    }
}
