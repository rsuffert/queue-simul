from queuesim import EXTERIOR
from pydantic import validate_call
import os
import yaml
from typing import Dict

class ConfigsValidationError(Exception):
    """
    Custom exception for configuration validation errors.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

@validate_call
def load_and_validate_configs(configs_path: str) -> dict:
    """
    Safely loads and validates the configuration file.
    Args:
        configs_path (str): The path to the configuration file.
    Returns:
        dict: The loaded configuration dictionary.
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ConfigsValidationError: If the configuration file is invalid or cannot be parsed.
    """
    if not os.path.exists(configs_path): raise FileNotFoundError(f"Configuration file {configs_path} not found")
    try:
        with open(configs_path, "r") as f:
            configs = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigsValidationError(f"Error parsing YAML configuration file: {e}")

    try:
        queues_configs = configs["queues"]
        network_configs = configs["network"]
        max_randoms = configs["max_randoms"]
        init_arrival_time = configs["init_arrival_time"]
    except KeyError as e:
        field = str(e).strip("'")
        raise ConfigsValidationError(f"'{field}': missing required field in configuration file")

    if not isinstance(queues_configs, list): raise ConfigsValidationError("'queues': must be a list")
    if len(queues_configs) == 0:             raise ConfigsValidationError("'queues': no queues defined in the configuration file")
    for idx, qc in enumerate(queues_configs):
        try:
            qc["servers"]
            qc["capacity"]
            qc["min_departure_time"]
            qc["max_departure_time"]
        except KeyError as e:
            field = str(e).strip("'")
            raise ConfigsValidationError(f"'queues[{idx}].{field}': missing required field in queue configuration")
        # initialize with default values
        if not "min_arrival_time" in qc: qc["min_arrival_time"] = 0.0
        if not "max_arrival_time" in qc: qc["max_arrival_time"] = 0.0
        # (further validation on the individual queue fields can be done when instantiating the Queue objects)
    
    if not isinstance(network_configs, list): raise ConfigsValidationError("'network': must be a list")
    from_to_probs: Dict[int, float] = {}
    for idx, nc in enumerate(network_configs):
        try:
            source = nc["source"]
            target = nc["target"]
            probab = nc["probability"]
        except KeyError as e:
            field = str(e).strip("'")
            raise ConfigsValidationError(f"'network[{idx}].{field}': missing required field in network configuration")
        if not isinstance(source, int):   raise ConfigsValidationError(f"'network[{idx}].source': must be an integer")
        if not isinstance(target, int):   raise ConfigsValidationError(f"'network[{idx}].target': must be an integer")
        if not isinstance(probab, float): raise ConfigsValidationError(f"'network[{idx}].probability': must be a float")
        if source < EXTERIOR:             raise ConfigsValidationError(f"'network[{idx}].source': must be a non-negative integer")
        if target < EXTERIOR:             raise ConfigsValidationError(f"'network[{idx}].target': must be a non-negative integer")
        if source >= len(queues_configs): raise ConfigsValidationError(f"'network[{idx}].source': must be less than the number of queues defined")
        if target >= len(queues_configs): raise ConfigsValidationError(f"'network[{idx}].target': must be less than the number of queues defined")
        if probab < 0.0 or probab > 1.0:  raise ConfigsValidationError(f"'network[{idx}].probability': probability must be between 0.0 and 1.0")
        if source not in from_to_probs: from_to_probs[source] = 0.0
        from_to_probs[source] += probab       
    for _, probab in from_to_probs.items():
        if probab < 0.0 or probab > 1.0:
            # we don't enforce that it's exactly 1.0 because we assume the missing portion
            # is the probability of going to the exterior (the client leaves the system)
            raise ConfigsValidationError(f"'network': total probability from queue {source} is {probab:.2f}, expected 1 (100%)")

    if not isinstance(max_randoms, int):         raise ConfigsValidationError("'max_randoms': must be an integer.")
    if not isinstance(init_arrival_time, float): raise ConfigsValidationError("'init_arrival_time': must be a float.")
    if max_randoms <= 0:                         raise ConfigsValidationError("'max_randoms': must be a positive integer.")
    if init_arrival_time < 0.0:                  raise ConfigsValidationError("'init_arrival_time': must be a non-negative float.")

    return configs