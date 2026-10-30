import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VULN_PATTERNS = [
    {
        "category": "Reentrancy",
        "cwe": "CWE-841",
        "severity": "CRITICAL",
        "description": "State update performed after external call allowing recursive re-entrant invocation.",
        "vulnerable_code": (
            "function withdraw() public {\n"
            "    uint amount = balances[msg.sender];\n"
            "    require(amount > 0);\n"
            "    (bool success, ) = msg.sender.call{value: amount}(\"\");\n"
            "    require(success);\n"
            "    balances[msg.sender] = 0;\n"
            "}"
        ),
        "patched_code": (
            "function withdraw() public nonReentrant {\n"
            "    uint amount = balances[msg.sender];\n"
            "    require(amount > 0);\n"
            "    balances[msg.sender] = 0; // Checks-Effects-Interactions\n"
            "    (bool success, ) = msg.sender.call{value: amount}(\"\");\n"
            "    require(success, \"Transfer failed\");\n"
            "}"
        )
    },
    {
        "category": "Access Control - Missing OnlyOwner",
        "cwe": "CWE-284",
        "severity": "HIGH",
        "description": "Privileged mint/burn or treasury withdrawal functions exposed without access control modifier.",
        "vulnerable_code": (
            "function setFeeRecipient(address newRecipient) public {\n"
            "    feeRecipient = newRecipient;\n"
            "}"
        ),
        "patched_code": (
            "function setFeeRecipient(address newRecipient) public onlyOwner {\n"
            "    require(newRecipient != address(0), \"Invalid zero address\");\n"
            "    feeRecipient = newRecipient;\n"
            "    emit FeeRecipientUpdated(newRecipient);\n"
            "}"
        )
    },
    {
        "category": "Oracle Manipulation / Spot Price Slippage",
        "cwe": "CWE-682",
        "severity": "CRITICAL",
        "description": "Protocol uses Uniswap spot reserve ratio directly as collateral price feed susceptible to flash loans.",
        "vulnerable_code": (
            "function getPrice() public view returns (uint256) {\n"
            "    (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();\n"
            "    return (uint256(reserve1) * 1e18) / uint256(reserve0);\n"
            "}"
        ),
        "patched_code": (
            "function getPrice() public view returns (uint256) {\n"
            "    // Chainlink decentralized aggregator with staleness checks\n"
            "    (, int256 price, , uint256 updatedAt, ) = priceFeed.latestRoundData();\n"
            "    require(price > 0 && block.timestamp - updatedAt < 3600, \"Stale price\");\n"
            "    return uint256(price);\n"
            "}"
        )
    },
    {
        "category": "Unchecked Return Value / Silent ERC20 Failure",
        "cwe": "CWE-252",
        "severity": "MEDIUM",
        "description": "Calling standard transfer/transferFrom without verifying boolean return or using SafeERC20.",
        "vulnerable_code": (
            "function payout(address token, address to, uint256 amount) external {\n"
            "    IERC20(token).transfer(to, amount);\n"
            "}"
        ),
        "patched_code": (
            "using SafeERC20 for IERC20;\n"
            "function payout(address token, address to, uint256 amount) external {\n"
            "    IERC20(token).safeTransfer(to, amount);\n"
            "}"
        )
    },
    {
        "category": "Solana Anchor Missing Account Check",
        "cwe": "CWE-285",
        "severity": "HIGH",
        "description": "Solana program fails to verify ownership or PDA seed derivation of account.",
        "vulnerable_code": (
            "#[derive(Accounts)]\n"
            "pub struct Withdraw<'info> {\n"
            "    pub vault: AccountInfo<'info>,\n"
            "    pub authority: Signer<'info>,\n"
            "}"
        ),
        "patched_code": (
            "#[derive(Accounts)]\n"
            "pub struct Withdraw<'info> {\n"
            "    #[account(mut, has_one = authority, seeds = [b\"vault\", authority.key().as_ref()], bump)]\n"
            "    pub vault: Account<'info, Vault>,\n"
            "    pub authority: Signer<'info>,\n"
            "}"
        )
    }
]

def generate_datasets(output_dir="engines/dataset-generator/data", sample_size=500, full_size=5000):
    os.makedirs(output_dir, exist_ok=True)
    sample_file = os.path.join(output_dir, "smart_contract_vulns_sample_500.jsonl")
    full_file = os.path.join(output_dir, "smart_contract_vulns_enterprise_full.jsonl")

    sample_records = []
    for i in range(sample_size):
        pattern = VULN_PATTERNS[i % len(VULN_PATTERNS)]
        rec = {
            "id": f"SC-VULN-{i+1:05d}",
            "ecosystem": "EVM" if "Solana" not in pattern["category"] else "Solana",
            "category": pattern["category"],
            "cwe_id": pattern["cwe"],
            "severity": pattern["severity"],
            "description": pattern["description"],
            "vulnerable_snippet": pattern["vulnerable_code"],
            "patched_snippet": pattern["patched_code"],
            "prompt": f"Audit the following smart contract code and identify any {pattern['category']} vulnerabilities:\n\n{pattern['vulnerable_code']}",
            "completion": f"### Vulnerability Analysis\n- Category: {pattern['category']} ({pattern['cwe']})\n- Severity: {pattern['severity']}\n- Explanation: {pattern['description']}\n\n### Patched Implementation:\n```solidity\n{pattern['patched_code']}\n```"
        }
        sample_records.append(rec)

    with open(sample_file, "w", encoding="utf-8") as f:
        for r in sample_records:
            f.write(json.dumps(r) + "\n")

    print(f"Generated {len(sample_records)} sample records -> {sample_file}")

    # Generate full dataset metadata manifest
    manifest = {
        "dataset_name": "smart-contract-vulnerabilities-and-patches-corpus",
        "sample_records_count": sample_size,
        "enterprise_records_count": full_size,
        "format": "JSONL / Parquet",
        "license": "Open Source Sample (MIT) / Commercial Enterprise Corpus",
        "commercial_url": "https://github.com/MilindChatrabhuji/edgesaas-starter-kit",
        "author": "Milind Chatrabhuji",
        "version": "1.0.0"
    }

    manifest_file = os.path.join(output_dir, "dataset_manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated manifest -> {manifest_file}")
    return sample_file, manifest_file

if __name__ == "__main__":
    generate_datasets()
