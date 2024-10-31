import copy
import random
import time
from pathlib import Path
from typing import Dict, List

from fameio.source.loader import load_yaml
from fameio.source.scenario import Contract
from fameio.source.tools import ensure_is_list

from scengen.cli import CreateOptions
from scengen.files import get_trace_file, save_seed_to_trace_file, write_yaml
from scengen.generation.digest import get_number_of_agents_to_create, get_agent_id, \
    update_series_paths, resolve_identifiers, resolve_ids, KEY_THIS_AGENT, REPLACEMENT_IDENTIFIER
from scengen.generation.check import _raise_if_static_contract, _raise_if_dynamic_match_missing
from scengen.generation.misc import get_matching_ids_from
from scengen.logs import log


DEBUG_NO_CREATE = "No agents to `create` found in Config '{}'"


class Generator:
    """Main scenario generator class"""
    def __init__(self, options: dict):
        self.options = options
        self.config = load_yaml(self.options[CreateOptions.CONFIG])
        self.trace_file = get_trace_file(self.config, options)
        self.scenario = {}

    def generate_scenarios(self) -> None:
        """Generates a new scenario based on `options` and `scenario_name` stored in `CreateOptions.DIRECTORY`"""
        log().debug("Generating scenario")
        self._init_random_seed()

        defaults = self.config["defaults"]
        count = self.trace_file["total_count"]
        self._set_scenario_name(defaults["base_name"] + f"_{count}")
        self._set_scenario(load_yaml(Path(self.options[CreateOptions.CONFIG].parent, self.config["base_template"])))

        if "create" in self.config:
            _raise_if_dynamic_match_missing(self.config["create"])
            self.add_agents()
            self.add_contracts()
        else:
            log().debug(DEBUG_NO_CREATE)

        resolve_identifiers(self.scenario, self.options)
        resolve_ids(self.scenario)
        update_series_paths(self.scenario, self.options, Path(self.config["base_template"]))

        self._set_scenario_path(Path(self.options[CreateOptions.DIRECTORY], self.options["scenario_name"] + ".yaml"))
        write_yaml(self.scenario, self.options["scenario_path"])

    def _init_random_seed(self) -> None:
        """Initializes random seed if not yet saved to `options['random_seed']`"""
        if not self.options.get("random_seed"):
            random_seed = self._get_random_seed()
            random.seed(random_seed + self.trace_file["total_count"])
            self.options["random_seed"] = self.trace_file["random_seed"] = random_seed
            save_seed_to_trace_file(self.options, random_seed)

    def _get_random_seed(self) -> int:
        """Returns random seed as integer, defined optionally in `defaults['seed']` or from system time in ns instead"""
        defaults = self.config["defaults"]
        if defaults.get("seed"):
            random_seed = defaults["seed"]
        else:
            random_seed = time.time_ns()
        return random_seed

    def _set_scenario_name(self, scenario_name: str) -> None:
        """Sets `scenario_name` in `options`"""
        self.options["scenario_name"] = scenario_name

    def _set_scenario(self, scenario: dict) -> None:
        """Sets `scenario`"""
        self.scenario = scenario

    def _set_scenario_path(self, path: Path) -> None:
        """Sets `scenario_name` in `options`"""
        self.options["scenario_path"] = path

    def add_agents(self) -> None:
        """Adds agents to create to `scenario`"""
        for agent in self.config["create"]:
            type_template = load_yaml(Path(self.options[CreateOptions.CONFIG].parent, agent["type_template"]))
            agent_type_template = type_template["Agent"]
            n_to_create = get_number_of_agents_to_create(agent["count"], self.options)
            agent_name = agent["this_agent"]

            for n in range(n_to_create):
                agent_to_append = copy.deepcopy(agent_type_template)
                agent_to_append["Id"] = get_agent_id(agent_name, n, n_to_create)
                self.scenario["Agents"].append(agent_to_append)

    def add_contracts(self) -> None:
        """
        Iterates over agents and adds contracts dynamically to `scenario`.
        Note: Ensure that all dynamic agents are already added to the scenario
        """
        for agent in self.config["create"]:
            type_template = load_yaml(Path(self.options[CreateOptions.CONFIG].parent, agent["type_template"]))
            if not type_template.get("Contracts"):
                continue
            id_map = {KEY_THIS_AGENT: get_matching_ids_from(self.scenario, ensure_is_list(agent["this_agent"]))}
            for id_key, id_values in agent.get("external_ids", {}).items():
                matched_ids = get_matching_ids_from(self.scenario, ensure_is_list(id_values))
                id_map[REPLACEMENT_IDENTIFIER + id_key] = matched_ids
            for contract in type_template.get("Contracts"):
                contract = Contract.from_dict(contract)
                _raise_if_static_contract(contract)
                contracts_to_append = self._create_contracts(contract, id_map)
                self.scenario["Contracts"].extend(contracts_to_append)

    @staticmethod
    def _create_contracts(contract: Contract, id_map: Dict) -> List[Dict]:
        """Returns list of dynamically created `contracts` based on template `contract` and `id_map`"""
        created_contracts = []
        sender_default = str(contract.sender_id)
        receiver_default = str(contract.receiver_id)
        for sender_override in id_map.get(sender_default, [sender_default]):
            for receiver_override in id_map.get(receiver_default, [receiver_default]):
                contract_to_append = copy.deepcopy(contract.to_dict())
                if REPLACEMENT_IDENTIFIER in sender_default:
                    # noinspection PyProtectedMember
                    contract_to_append[Contract._KEY_SENDER] = sender_override
                if REPLACEMENT_IDENTIFIER in receiver_default:
                    # noinspection PyProtectedMember
                    contract_to_append[Contract._KEY_RECEIVER] = receiver_override
                created_contracts.append(contract_to_append)
        return created_contracts
