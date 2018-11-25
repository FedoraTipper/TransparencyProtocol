var web3 = new Web3(new Web3.providers.HttpProvider("https://ropsten.infura.io/v3/e3edb56114244a31b698dd92dc7cfcf7"));
//web3.eth.defaultAccount = web3.eth.accounts[0];

var myContractAddress = "0xD946eddE77A7486321D9445EC78f7b1ea0B9EA53";

var myABI = JSON.parse('[{"constant": false,"inputs": [{"name": "destination","type": "address"},{"name": "updateid","type": "bytes32"},{"name": "payload","type": "string"}],"name": "addRecord","outputs": [],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [{"name": "txid","type": "bytes32"}],"name": "getRecord","outputs": [{"name": "timestamp","type": "uint256"},{"name": "source","type": "address"},{"name": "destination","type": "address"},{"name": "updateid","type": "bytes32"},{"name": "payload","type": "string"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "getRecordIDs","outputs": [{"name": "","type": "bytes32[]"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "getRecordNumber","outputs": [{"name": "","type": "uint256"}],"payable": false,"stateMutability": "nonpayable","type": "function"}]');

var myContract = new web3.eth.Contract(myABI, myContractAddress);

function addRecord(){
	var dst = document.getElementById("dstField2").value;
	var uID = document.getElementById("uIDField2").value;
	var payload = document.getElementById("payloadField2").value;
	nonce = 0;
	var ownerAddress = '0xE7050595076bF3d06F8847B350eaaa4a7616a39a';
	var privateKey = "0xed1c453893abf4f773867f4ba4e84fb08d7b2696c8689474b076978f3ba3284f";
	var encodedABI = myContract.methods.addRecord(dst, uID, payload).encodeABI();
	web3.eth.getTransactionCount(ownerAddress)
	.then(function (n){
		nonce = n;
	});

	myContract.methods.addRecord(dst, uID, payload).estimateGas({from: ownerAddress}, (error, gasEstimate) =>{
		let tx = {
			to: myContractAddress,
			chainId: 3,
			gas: 1000000,
			data: encodedABI,
			nonce: nonce
		};
		web3.eth.accounts.signTransaction(tx, privateKey, (err, resp) => {
			if (resp == null){}
			else{
				let tran = web3.eth.sendSignedTransaction(resp.rawTransaction);
				tran.on('transactionHash', (txhash) => {
					document.getElementById("txIDField").innerHTML = txhash;
					document.getElementById("txIDField").setAttribute('href', "https://ropsten.etherscan.io/tx/" + txhash);
					document.getElementById("resultDiv").removeAttribute("hidden");
				});
			}
		})
	});
}


function displayRecordIDs(){
	document.getElementById("TXList").innerHTML = "";
	var records = "";
	myContract.methods.getRecordIDs().call()
	.then(function (records){
		for (var i = 0; i < records.length; i++){
			document.getElementById("TXList").innerHTML = document.getElementById("TXList").innerHTML + "<li href='#' onclick=displayRecord('"+records[i]+"') class='list-group-item'>"+records[i]+"</li>";
		}
	});
}

function displayRecord(ID){
	myContract.methods.getRecord(ID).call()
	.then(function (record){
		var timestamp = record[0];
		var src = record[1];
		var dst = record[2];
		var uID = record[3];
		var payload = record[4];
		document.getElementById("srcField").value = src;
		document.getElementById("dstField").value = dst;
		document.getElementById("uIDField").value = uID;
		document.getElementById("timestampField").value = timestamp;
		document.getElementById("payloadField").innerHTML = payload;
		document.getElementById("recordDiv").removeAttribute("hidden");
	});
}
