import re


def is_valid_wallet_address(value):
	if not isinstance(value, str):
		return False
	return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", value.strip()))