var web3 = new Web3(new Web3.providers.HttpProvider("https://ropsten.infura.io/v3/77fef628eecc447ab8bf67e7990dc090"));
//web3.eth.defaultAccount = web3.eth.accounts[0];

var proxy = "https://cors-anywhere.herokuapp.com/";
var APIHOSTIP = "http://178.128.43.198:5002";
var myContractAddress = "0x7e55ebD9C7b6aA3b63D1A303e61FF11472E16F76";

var myABI = JSON.parse('[{"constant": false,"inputs": [{"name": "destination","type": "address"},{"name": "updateid","type": "bytes32"},{"name": "payload","type": "string"}],"name": "addRecord","outputs": [],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [{"name": "txid","type": "bytes32"}],"name": "getRecord","outputs": [{"name": "timestamp","type": "uint256"},{"name": "source","type": "address"},{"name": "destination","type": "address"},{"name": "updateid","type": "bytes32"},{"name": "payload","type": "string"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "getRecordIDs","outputs": [{"name": "","type": "bytes32[]"}],"payable": false,"stateMutability": "nonpayable","type": "function"},{"constant": false,"inputs": [],"name": "getRecordNumber","outputs": [{"name": "","type": "uint256"}],"payable": false,"stateMutability": "nonpayable","type": "function"}]');

var myContract = new web3.eth.Contract(myABI, myContractAddress);

var ownerAddress = "0xd93cE60e2dC209926fFcE0Bae474d19fC9933BE5";
var privateKey = "0xb5c3d2968ac5bafae1d8c5ff01c50d6f95c4272fc9bb193e5614ca4f2a0b3fd3";


function hexToBytes(hex) {
    for (var bytes = [], c = 0; c < hex.length; c += 2)
    bytes.push(parseInt(hex.substr(c, 2), 16));
    return bytes;
}



function addRecord(){
	var dst = document.getElementById("dstField2").value;
	var uID = document.getElementById("uIDField2").value;


	var payload = document.getElementById("payloadField2").value;
	nonce = 0;
	var encodedABI = myContract.methods.addRecord(dst, uID, payload).encodeABI();
	web3.eth.getTransactionCount(ownerAddress)
	.then(function (n){
		nonce = n;
	});

	myContract.methods.addRecord(dst, uID, payload).estimateGas({from: ownerAddress}, (error, gasEstimate) =>{
		let tx = {
			to: myContractAddress,
			chainId: 3,
			gas: 210000,
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
	document.getElementById("pubkeyField").innerHTML = ownerAddress;
	document.getElementById("pubkeyField").setAttribute('href', "https://ropsten.etherscan.io/address/" + ownerAddress);

	var records = "";
	myContract.methods.getRecordIDs().call()
	.then(function (records){
		if (records.length == 0){
			document.getElementById("TXList").innerHTML = "<li class='list-group-item'>No records</li>";
		}else{
			for (var i = 0; i < records.length; i++){
				document.getElementById("TXList").innerHTML = document.getElementById("TXList").innerHTML + "<li href='#' onclick=displayRecord('"+records[i]+"') class='list-group-item'>"+records[i]+"</li>";
			}
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
		if (payload == ""){
			payload = "<Empty Payload>";
		}

		url = APIHOSTIP + '/ranks/' + src;
		url2 = APIHOSTIP + '/ranks/' + dst;

		setRank(src)
		.then(function (rank){
			setRank(dst)
			.then(function (rank2){
			 	document.getElementById("srcRankField").value = rank['data'][0]['rank'];
			 	document.getElementById("dstRankField").value = rank2['data'][0]['rank'];
				document.getElementById("srcField").value = src;
				document.getElementById("dstField").value = dst;
				document.getElementById("uIDField").value = uID;
				document.getElementById("timestampField").value = timestamp;
				document.getElementById("payloadField").innerHTML = payload;
				document.getElementById("recordDiv").removeAttribute("hidden");
			});
		});

		
	});
}

async function setRank(src){
	response = await fetch(proxy + APIHOSTIP + '/ranks/' + src);
	myJson = await response.json();
	return myJson;
}