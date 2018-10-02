pragma solidity ^0.4.4;

contract Record {
    // Create a custom array for records which is held within the contract. It is indexed by 32 byte strings (Transaction ID, see below)
    mapping (bytes32 => record) records;
    // Create an array for all record IDshttp://192.168.1.3:90/
    bytes32[] recordsByID;
    // Magic number used for our hashing algorithm
    uint nonce = 0;

    // Create a simple object like data structure
    struct record{
        uint timestamp;
        address source;
        address destination;
        bytes32 updateid;
        string payload;
    }

    function addRecord (address destination, bytes32 updateid, string payload) public{
        // Entities aren't able to create a record about themselves.
        // Require will validate this constraint, if constraint is true then the contract will refund all ether (that is not spent) back to the entity who made the transaction. 
        require(destination != msg.sender);
        // We create an unique ID in a form of 32 bytes. Since EVM does not house any PRNG algorithms. We need to create one for ourselves.
        // Encode everything together, since keccak only takes single byte data
        bytes32 txid = keccak256(abi.encodePacked(msg.sender, destination, block.difficulty, msg.data, nonce++));
        // We can only set the timestamp to the receent block's timestamp
        records[txid].timestamp = block.timestamp;
        // Get the address of the sender
        records[txid].source = msg.sender;
        records[txid].destination = destination;
        records[txid].updateid = updateid;
        records[txid].payload = payload;
        // Push the transaction ID into a premade array, which we will use to return all TX ids at once.
        recordsByID.push(txid);
    }
    
    // Return all transcation/record IDs
    function getRecordIDs() public returns (bytes32[]){
        return recordsByID;
    }
    
    // Return the number of records held in the contract
    function getRecordNumber() public returns (uint){
        return recordsByID.length;
    }
    
    //Return Record data which is indexed from a given 32 byte input
    function getRecord(bytes32 txid) public returns (uint timestamp, address source, address destination, bytes32 updateid, string payload){
        return(records[txid].timestamp, records[txid].source, records[txid].destination, records[txid].updateid, records[txid].payload);
    }
}