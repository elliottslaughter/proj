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
    scan_repo_for_files,
    UnrecognizedFile,
    IncompleteGroup,
)
from .trees import (
    PathTree,
    FileTree,
    MutableFileTreeWithMtime,
    load_filesystem_for_repo,
)
from .paths import (
    File,
    RoleInGroup,
    RepoRelPath,
)
from .ifndef import (
    get_current_ifndef,
    get_correct_ifndef_for_path,
)
from .unparse_project import (
    get_repo_rel_path,
)
from .includes import (
    get_include_path,
    get_generated_include_path,
    find_includes_in_cpp_file_contents,
    get_include_path_for_file,
)

_l = logging.getLogger(__name__)


class Check(StrEnum):
    FORMAT = "format"
    CPU_CI = "cpu-ci"
    GPU_CI = "gpu-ci"
    LAYOUT = "layout"
    INCLUDE = "include"
    IFNDEF = "ifndef"

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
            path: RepoRelPath = get_repo_rel_path(error.path, extension_config=extension_config)
            _l.warn('Unrecognized file at %s', path)
            failed = True
    if failed:
        fail_with_error("Layout check failed.")

def run_include_check(
    repo_path_tree: FileTree,
    extension_config: ExtensionConfig,
) -> None:
    valid_include_paths = set()
    for file in scan_repo_for_files(repo_path_tree, extension_config):
        if isinstance(file, File):
            match file.role:
                case RoleInGroup.PUBLIC_HEADER:
                    valid_include_paths.add(get_include_path(file.group, header_extension=extension_config.header_extension))
                case RoleInGroup.DTGEN_TOML:
                    valid_include_paths.add(get_generated_include_path(file.group, header_extension=extension_config.header_extension))
    
    failed = False
    for file in scan_repo_for_files(repo_path_tree, extension_config):
        if isinstance(file, File):
            match file.role:
                case RoleInGroup.DTGEN_TOML:
                    valid_include_paths.add(get_include_path(file.group, header_extension=extension_config.header_extension))
                case _:
                    contents = repo_path_tree.get_file_contents(
                        get_repo_rel_path(file, extension_config).path 
                    )
                    includes = find_includes_in_cpp_file_contents(
                        contents,
                        header_extension=extension_config.header_extension, 
                    )
                    for include in includes:
                        if isinstance(include, File):
                            include_path = get_include_path_for_file(include, header_extension=extension_config.header_extension)
                            if include_path not in valid_include_paths:
                                _l.warning('Found invalid include in %s: %s does not exist', file, include)
                                failed = True
    if failed:
        fail_with_error("Include check failed.")
          

def run_ifndef_check(
    repo_path_tree: FileTree,
    ifndef_base: str,
    extension_config: ExtensionConfig,
) -> None:
    failed = False
    for file in scan_repo_for_files(repo_path_tree, extension_config):
        if isinstance(file, File):
            if file.role != RoleInGroup.PUBLIC_HEADER:
                continue
            file_path = get_repo_rel_path(file, extension_config)
            contents = repo_path_tree.get_file_contents(file_path.path)
            curr_ifndef = get_current_ifndef(contents)
            correct_ifndef = get_correct_ifndef_for_path(ifndef_base, file_path)
            if curr_ifndef != correct_ifndef:
                _l.warn('Incorrect ifndef in file %s: %s (current) != %s (correct)', file, curr_ifndef, correct_ifndef)
                failed = True
    if failed:
        fail_with_error("Ifndef check failed.")

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
    elif check == Check.IFNDEF:
        run_ifndef_check(
            repo_file_tree,
            config.ifndef_name,
            config.extension_config,
        )
    elif check == Check.INCLUDE:
        return run_include_check(
            repo_file_tree,
            config.extension_config,
        )


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
