from typing import List
import numpy as np

def aggregate_variants_results(results: List[dict]):
    """
    Aggregate the results of multiple variants.

    Args:
        results (List[dict]): A list of dictionaries containing the results for each variant.

    Returns:
        dict: A dictionary containing the aggregated results, with the metric names as keys and the aggregated values as values.
    """
    aggregate_results = {}
    for result in results:
        for name, value in result.items():
            if name not in aggregate_results.keys():
                aggregate_results[name] = []
            try:
                float_val = float(value)
            except Exception:
                float_val = np.nan
            aggregate_results[name].append(float_val)

    for name, value in aggregate_results.items():
        metric_name = name
        aggregate_results[name] = np.nanmean(value)
        if "pass_rate" in metric_name:
            metric_name = metric_name + "(%)"
            aggregate_results[name] = aggregate_results[name] * 100.0
        aggregate_results[name] = round(aggregate_results[name], 2)
        print(f"Metric {metric_name}: {aggregate_results[name]}")  # Replace with logging to your preferred system

    return aggregate_results
