# ETH Provenance
ETH Provenance is a decentralized service that allows you to store an online distributed proof of existence for any data (document, image, etc.) on the Ethereum blockchain. By storing a cryptographic hash of your data on the blockchain, you can later certify that the data existed at a certain time without revealing the actual data or your identity.

The key advantages of using ETH Provenance are anonymity, privacy, and decentralization. Your document's existence is permanently validated by the Ethereum blockchain, so you don't need to trust any central authority. This makes ETH Provenance useful for various applications, such as:

  * Demonstrating data ownership without revealing the actual data, which can be useful for copyrighted material, patents, etc.
  * Document timestamping, where you can prove that certain data existed at a certain moment in time without relying on a central authority.
  * Checking for data integrity, where you can ensure that data has not been modified since it was timestamped on the Ethereum blockchain.

## Technical Foundations
ETH Provenance certifies a data by embedding its SHA256 digest in the Ethereum blockchain. This is done by generating a special Ethereum transaction that encodes the hash in the transaction data. This transaction on the Ethereum blockchain is then live on the blockchain.

Once the transaction is confirmed, the data is permanently certified and proven to exist at least as early as the time the transaction was confirmed. If the data hadn't existed at the time the transaction entered the blockchain, it would have been impossible to embed its digest in the transaction. Embedding some hash and then adapting a future document to match the hash is also impossible due to the pre-image resistance of hash functions.

If anyone wants to manually confirm the document's existence at the timestamped time, they should just follow these steps:

  1 Calculate the document's SHA256 digest.
  2 Find a transaction the Ethereum blockchain containing the document's hash.
  3 The existence of that transaction in the blockchain proves that the document existed at the time the transaction was confirmed.

By using ETH Provenance, you can be sure that your document's existence is permanently validated by the Ethereum blockchain, which is a decentralized and trustless network.
