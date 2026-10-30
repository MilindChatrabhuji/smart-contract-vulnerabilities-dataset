---
license: mit
task_categories:
  - text2text-generation
  - text-classification
language:
  - en
tags:
  - smart-contracts
  - security
  - solidity
  - web3
  - code-vulnerabilities
  - cwe
size_categories:
  - 1K<n<10K
pretty_name: "Smart Contract Vulnerabilities & Patches Corpus (5,000+ Verified Records)"
---

# 🛡️ Smart Contract Vulnerabilities & Patches Corpus

[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Datasets-yellow)](https://huggingface.co/datasets/MilindChatrabhuji/smart-contract-vulns-and-patches)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A curated, fine-tuning and evaluation dataset containing verified smart contract security vulnerabilities paired with before-and-after diff patches across EVM (Solidity) and Solana (Rust/Anchor).

## Dataset Summary

Fine-tuning LLMs for automated smart contract auditing and automated bug patching requires high-quality, non-synthetic vulnerability pairings. This dataset compiles real-world exploit patterns mapped directly to **Common Weakness Enumeration (CWE)** standards.

### Supported Vulnerability Categories
- **Reentrancy (CWE-841)**: Checks-Effects-Interactions violations and mutex locks.
- **Access Control & Missing OnlyOwner (CWE-284)**: Unprotected treasury and mint controls.
- **Oracle Manipulation & Spot Price Slippage (CWE-682)**: AMM reserves vs. decentralized TWAP/Chainlink price feeds.
- **Unchecked Return Values (CWE-252)**: Silent ERC-20 boolean transfer failures.
- **Solana Anchor Account Verification (CWE-285)**: Missing PDA seeds, owner, and authority checks.

---

## Dataset Structure

### Features
```json
{
  "id": "SC-VULN-00001",
  "ecosystem": "EVM",
  "category": "Reentrancy",
  "cwe_id": "CWE-841",
  "severity": "CRITICAL",
  "description": "State update performed after external call allowing recursive re-entrant invocation.",
  "vulnerable_snippet": "function withdraw() public { ... }",
  "patched_snippet": "function withdraw() public nonReentrant { ... }",
  "prompt": "Audit the following smart contract code...",
  "completion": "### Vulnerability Analysis\n- Category: Reentrancy..."
}
```

---

## Free Open-Source Sample vs. Enterprise Corpus

- **Open-Source Sample (500 Records)**: Free download via Hugging Face Hub (JSONL / Parquet format).
- **Enterprise Fine-Tuning Corpus (5,000+ Records)**:
  - Includes full codebase contexts, AST graphs, vector embeddings, and multi-file dependencies.
  - Available for direct instant commercial download at [NexusPulse Data Store](https://github.com/MilindChatrabhuji/edgesaas-starter-kit).

## Usage with Hugging Face Datasets

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="smart_contract_vulns_sample_500.jsonl")
print(dataset["train"][0])
```

## License
MIT License. Created & curated by [Milind Chatrabhuji](https://github.com/MilindChatrabhuji).
