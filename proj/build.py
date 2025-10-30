from .config_file import ProjectConfig
from typing import (
    Iterable,
)
import logging
import sys
import os
from pathlib import Path
from .failure import fail_with_error
from .targets import (
    BuildTarget,
)
from .subprocess_invocation import SubprocessInvocation
from .paths import Repo
from .trees import PathTree
import subprocess

_l = logging.getLogger(__name__)


def build_targets(
    repo: Repo,
    repo_path_tree: PathTree,
    config: ProjectConfig,
    targets: Iterable[BuildTarget],
    jobs: int,
    verbosity: int,
    build_dir: Path,
) -> None:
    _targets = list(sorted(set([t.name for t in targets])))
    _l.info("Building targets: %s", _targets)
    if len(_targets) == 0:
        fail_with_error("No build targets selected")
    
    result = subprocess.run(
        [
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
        # stderr=sys.stdout,
    )
    # sys.stdout.flush()
    result.check_returncode()

    # SubprocessInvocation(
    #     cmd=[
    #         "make",
    #         "-C",
    #         str(build_dir),
    #         "-j",
    #         str(jobs),
    #         *_targets,
    #     ],
    #     env={
    #         **os.environ,
    #         "CCACHE_BASEDIR": str(config.base),
    #         **({"VERBOSE": "1"} if verbosity <= logging.DEBUG else {}),
    #     },
    #     stderr=sys.stdout,
    # ).check_call()
