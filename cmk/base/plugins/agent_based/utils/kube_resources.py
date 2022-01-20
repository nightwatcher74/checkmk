#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2022 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import json
from typing import Callable, Iterable, Literal, Optional, Tuple, TypedDict, Union

from pydantic import BaseModel

from cmk.base.plugins.agent_based.agent_based_api.v1 import check_levels, Metric, render, Result
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, StringTable

ResourceType = Literal["memory", "cpu"]
RequirementType = Literal["request", "limit", "allocatable"]
AllocatableKubernetesObject = Literal["cluster", "node"]


class Resources(BaseModel):
    """sections: "[kube_memory_resources_v1, kube_cpu_resources_v1]"""

    request: float
    limit: float
    count_unspecified_requests: int
    count_unspecified_limits: int
    count_zeroed_limits: int
    count_total: int


class AllocatableResource(BaseModel):
    """sections: [kube_allocatable_cpu_resource_v1, kube_allocatable_memory_resource_v1]"""

    context: AllocatableKubernetesObject
    value: float


def count_overview(resources: Resources, requirement: RequirementType) -> str:
    ignored = (
        resources.count_unspecified_requests
        if requirement == "request"
        else resources.count_unspecified_limits + resources.count_zeroed_limits
    )
    return (
        f"{resources.count_total - ignored}/{resources.count_total} containers with {requirement}s"
    )


def parse_resources(string_table: StringTable) -> Resources:
    """Parses limit and request values into Resources
    >>> parse_resources([['{"request": 209715200.0,'
    ... '"limit": 104857600.0,'
    ... '"count_unspecified_requests": 0,'
    ... '"count_unspecified_limits": 0,'
    ... '"count_zeroed_limits": 1,'
    ... '"count_total": 1}']])
    Resources(request=209715200.0, limit=104857600.0, count_unspecified_requests=0, count_unspecified_limits=0, count_zeroed_limits=1, count_total=1)
    """
    return Resources(**json.loads(string_table[0][0]))


def parse_allocatable_resource(string_table: StringTable) -> AllocatableResource:
    """Parses allocatable value into AllocatableResource
    >>> parse_allocatable_resource([['{"context": "node", "value": 23120704.0}']])
    AllocatableResource(context='node', value=23120704.0)
    >>> parse_allocatable_resource([['{"context": "cluster", "value": 6.0}']])
    AllocatableResource(context='cluster', value=6.0)
    """
    return AllocatableResource(**json.loads(string_table[0][0]))


class Usage(BaseModel):
    usage: float


Param = Union[Literal["no_levels"], Tuple[Literal["levels"], Tuple[float, float]]]


class Params(TypedDict):
    usage: Param
    request: Param
    limit: Param
    cluster: Param
    node: Param


DEFAULT_PARAMS = Params(
    usage="no_levels",
    request="no_levels",
    limit="no_levels",
    cluster="no_levels",
    node="no_levels",
)


def check_with_utilization(
    usage: float,
    resource_type: ResourceType,
    requirement_type: RequirementType,
    kubernetes_object: Optional[AllocatableKubernetesObject],
    requirement_value: float,
    params: Params,
    render_func: Callable[[float], str],
) -> Iterable[Union[Metric, Result]]:
    utilization = usage * 100.0 / requirement_value
    if kubernetes_object is None:
        metric_name = f"kube_{resource_type}_{requirement_type}_utilization"
        assert requirement_type != "allocatable"
        param = params[requirement_type]
        title = requirement_type.title()
    else:
        metric_name = f"kube_{resource_type}_{kubernetes_object}_{requirement_type}_utilization"
        param = params[kubernetes_object]
        title = kubernetes_object.title()
    result, metric = check_levels(
        utilization,
        levels_upper=param[1] if param != "no_levels" else None,
        metric_name=metric_name,
        render_func=render.percent,
        boundaries=(0.0, None),
    )
    assert isinstance(result, Result)
    percentage, *warn_crit = result.summary.split()
    yield Result(
        state=result.state,
        summary=" ".join(
            [
                f"{title} utilization: {percentage} - {render_func(usage)} of {render_func(requirement_value)}"
            ]
            + warn_crit
        ),
    )
    yield metric


def requirements_for_object(
    resources: Resources, allocatable_resource: Optional[AllocatableResource]
) -> Iterable[Tuple[RequirementType, Optional[AllocatableKubernetesObject], float]]:
    yield "request", None, resources.request
    yield "limit", None, resources.limit
    if allocatable_resource is not None:
        yield "allocatable", allocatable_resource.context, allocatable_resource.value


def check_resource(
    params: Params,
    usage: Optional[Usage],
    resources: Resources,
    allocatable_resource: Optional[AllocatableResource],
    resource_type: ResourceType,
    render_func: Callable[[float], str],
) -> CheckResult:
    if usage is not None:
        total_usage = usage.usage
        yield from check_levels(
            total_usage,
            label="Usage",
            levels_upper=params["usage"][1] if params["usage"] != "no_levels" else None,
            metric_name=f"kube_{resource_type}_usage",
            render_func=render_func,
            boundaries=(0.0, None),
        )
    for requirement_type, kubernetes_object, requirement in requirements_for_object(
        resources, allocatable_resource
    ):
        if requirement != 0.0 and usage is not None:
            result, metric = check_with_utilization(
                total_usage,
                resource_type,
                requirement_type,
                kubernetes_object,
                requirement,
                params,
                render_func,
            )
            yield Metric(f"kube_{resource_type}_{requirement_type}", requirement)
        else:  # requirements with no usage
            result, metric = check_levels(
                requirement,
                label=requirement_type.title(),
                metric_name=f"kube_{resource_type}_{requirement_type}",
                render_func=render_func,
                boundaries=(0.0, None),
            )
        assert isinstance(result, Result)
        summary = result.summary
        if requirement_type in ["request", "limit"]:
            summary = f"{result.summary} ({count_overview(resources, requirement_type)})"
        yield Result(state=result.state, summary=summary)
        yield metric
