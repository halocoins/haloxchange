const { EthereumProvider } = require("@walletconnect/ethereum-provider");


window.ethProvider = async function (){
    const provider = await EthereumProvider.init({
        projectId: '', // REQUIRED your projectId
        chains: [56], // REQUIRED chain ids
        showQrModal: true, // REQUIRED set to "true" to use @walletconnect/modal
    })

    return provider;
}
