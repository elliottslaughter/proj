from typing import (
    Optional,
    Sequence,
)
from os import (
    PathLike,
)
from enum import (
    StrEnum,
)
from .config_file import (
    ProjectConfig,
    ExtensionConfig,
)
from .format import (
    run_formatter_check as _run_formatter_check,
)
from .dtgen import (
    run_dtgen,
)
from .cmake import (
    cmake_all,
)
import multiprocessing
from .build import (
    build_targets,
)
from .testing import (
    run_test_suites,
)
import logging
from .failure import (
    fail_without_error,
    fail_with_error,
)
from . import subprocess_trace as subprocess
from .layout import (
    run_layout_check as _run_layout_check,
    UnrecognizedFile,
    IncompleteGroup,
)
from .trees import (
    PathTree,
    MutableFileTreeWithMtime,
    load_filesystem_for_repo,
)

_l = logging.getLogger(__name__)


class Check(StrEnum):
    FORMAT = "format"
    CPU_CI = "cpu-ci"
    GPU_CI = "gpu-ci"
    LAYOUT = "layout"

def run_layout_check(
    repo_path_tree: PathTree,
    extension_config: ExtensionConfig,
) -> None:
    failed = False
    for error in _run_layout_check(repo_path_tree, extension_config):
        if isinstance(error, IncompleteGroup):
            _l.warn('Incomplete file group %s: missing %s', error.file_group, ', '.join(map(str, (error.missing))))
            failed = True
        elif isinstance(error, UnrecognizedFile):
            _l.warn('Unrecognized file at %s', error.path)
            failed = True
    if failed:
        fail_with_error("Layout check failed.")


def run_formatter_check(
    config: ProjectConfig, files: Optional[Sequence[PathLike[str]]] = None
) -> None:
    try:
        _run_formatter_check(config=config, files=files)
    except subprocess.CalledProcessError:
        fail_with_error("Formatter check failed. You should probably run 'proj format'")


def run_check(config: ProjectConfig, check: Check, verbosity: int) -> None:
    repo_file_tree = load_filesystem_for_repo(config.repo)

    if check == Check.FORMAT:
        run_formatter_check(config)
    elif check == Check.LAYOUT:
        run_layout_check(repo_file_tree, config.extension_config)
    elif check == Check.CPU_CI:
        run_cpu_ci(config, verbosity=verbosity)
    elif check == Check.GPU_CI:
        run_gpu_ci(config, verbosity=verbosity)


def run_build_check(config: ProjectConfig, repo_file_tree: MutableFileTreeWithMtime, verbosity: int) -> None:
    run_dtgen(
        repo=config.repo,
        repo_file_tree=repo_file_tree,
        force=True,
        extension_config=config.extension_config,
        ifndef_base=config.ifndef_name,
    )
    cmake_all(config, fast=False, trace=False)

    build_targets(
        repo=config.repo, 
        repo_path_tree=repo_file_tree,
        config=config,
        targets=config.all_build_targets,
        jobs=multiprocessing.cpu_count(),
        verbosity=verbosity,
        build_dir=config.debug_build_dir,
    )


def run_cpu_ci(config: ProjectConfig, verbosity: int) -> None:
    repo_file_tree = load_filesystem_for_repo(config.repo)

    _l.info("Running formatter check...")
    run_formatter_check(config)

    _l.info("Running dtgen --force...")
    run_dtgen(
        repo=config.repo,
        repo_file_tree=repo_file_tree,
        force=True,
        extension_config=config.extension_config,
        ifndef_base=config.ifndef_name,
    )
    _l.info("Running cmake...")
    cmake_all(config, fast=False, trace=False)

    cpu_build_targets = [t.build_target for t in config.all_cpu_test_targets]
    _l.info("Building %s", cpu_build_targets)
    build_targets(
        repo=config.repo,
        repo_path_tree=repo_file_tree,
        config=config,
        targets=cpu_build_targets,
        jobs=multiprocessing.cpu_count(),
        verbosity=verbosity,
        build_dir=config.coverage_build_dir,
    )

    _l.info("Running tests %s", config.all_cpu_test_targets)
    test_results = run_test_suites(
        config=config,
        test_suites=list(sorted(config.all_cpu_test_targets)),
        build_dir=config.coverage_build_dir,
        debug=False,
    )

    if len(test_results.failed) > 0:
        fail_without_error()


def run_gpu_ci(config: ProjectConfig, verbosity: int) -> None:
    repo_file_tree = load_filesystem_for_repo(config.repo)

    _l.info("Running dtgen")
    run_dtgen(
        repo=config.repo,
        repo_file_tree=repo_file_tree,
        force=True,
        extension_config=config.extension_config,
        ifndef_base=config.ifndef_name,
    )
    _l.info("Running cmake")
    cmake_all(config, fast=False, trace=False)

    cuda_build_targets = [t.build_target for t in config.all_cuda_test_targets]
    _l.info("Building targets %", cuda_build_targets)
    build_targets(
        repo=config.repo,
        repo_path_tree=repo_file_tree,
        config=config,
        targets=cuda_build_targets,
        jobs=multiprocessing.cpu_count(),
        verbosity=verbosity,
        build_dir=config.debug_build_dir,
    )

    test_suites = list(sorted(config.all_cuda_test_targets))
    _l.info("Running test suites %s", test_suites)
    test_results = run_test_suites(
        config=config,
        test_suites=test_suites,
        build_dir=config.debug_build_dir,
        debug=False,
    )

    if len(test_results.failed) > 0:
        fail_without_error()
