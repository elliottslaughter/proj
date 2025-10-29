from .config_file import ProjectConfig
from typing import (
    Iterable,
)
from . import subprocess_trace as subprocess
import logging
import sys
import os
from pathlib import Path
from .failure import fail_with_error
from .dtgen import run_dtgen
from .targets import (
    BuildTarget,
)
from .subprocess_invocation import SubprocessInvocation
from .paths import Repo
from .trees import PathTree

_l = logging.getLogger(__name__)


def build_targets(
    repo: Repo,
    repo_path_tree: PathTree,
    config: ProjectConfig,
    targets: Iterable[BuildTarget],
    jobs: int,
    verbosity: int,
    build_dir: Path,
) -> SubprocessInvocation:
    _targets = list(sorted(set([t.name for t in targets])))
    _l.info("Building targets: %s", _targets)
    if len(_targets) == 0:
        fail_with_error("No build targets selected")

    # if not dtgen_skip:
    #     run_dtgen(
    #         repo=repo,
    #         config=config,
    #         root=config.base,
    #         config=config,
    #         force=False,
    #     )

    return SubprocessInvocation(
        cmd=[
            "make",
            "-C",
            str(build_dir),
            "-j",
            str(jobs),
            *_targets,
        ],
        env={
            **os.environ,
            "CCACHE_BASEDIR": str(config.base),
            **({"VERBOSE": "1"} if verbosity <= logging.DEBUG else {}),
        },
        stderr=sys.stdout,
    )
