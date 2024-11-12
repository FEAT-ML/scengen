from fameio.source.scenario import Contract
from fameio.source.tools import ensure_is_list

from scengen.generation.digest import ERR_STATIC_CONTRACT, ERR_MISSING_MATCH, REPLACEMENT_IDENTIFIER
from scengen.logs import log_and_raise_critical


def raise_if_static_contract(contract: Contract) -> None:
    """Raises Error if `contract` is static, e.g. has neither dynamic `sender_id` nor `receiver_id`"""
    sender = str(contract.sender_id)
    receiver = str(contract.receiver_id)
    identifier_missing = REPLACEMENT_IDENTIFIER not in sender and REPLACEMENT_IDENTIFIER not in receiver
    if identifier_missing:
        log_and_raise_critical(ERR_STATIC_CONTRACT.format(contract))


def raise_if_dynamic_match_missing(create_config: list[dict]) -> None:
    """Raises Error if any external id(s) cannot be matched to dynamically created agents - skips integer ids"""
    agent_aliases = [config["this_agent"] for config in create_config]
    for config in create_config:
        missing_ids = []
        for external_id_key, external_id_values in config.get("external_ids", {}).items():
            for entry in ensure_is_list(external_id_values):
                if entry not in agent_aliases and isinstance(entry, str):
                    missing_ids.append(entry)
        if missing_ids:
            log_and_raise_critical(ERR_MISSING_MATCH.format(missing_ids, agent_aliases))
