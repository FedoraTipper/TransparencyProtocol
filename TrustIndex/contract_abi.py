abi = """[
    {
        "constant": false,
        "inputs": [
            {
                "name": "destination",
                "type": "address"
            },
            {
                "name": "updateid",
                "type": "bytes32"
            },
            {
                "name": "payload",
                "type": "string"
            }
        ],
        "name": "addRecord",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "txid",
                "type": "bytes32"
            }
        ],
        "name": "getRecord",
        "outputs": [
            {
                "name": "timestamp",
                "type": "uint256"
            },
            {
                "name": "source",
                "type": "address"
            },
            {
                "name": "destination",
                "type": "address"
            },
            {
                "name": "updateid",
                "type": "bytes32"
            },
            {
                "name": "payload",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [],
        "name": "getRecordIDs",
        "outputs": [
            {
                "name": "",
                "type": "bytes32[]"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [],
        "name": "getRecordNumber",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
"""