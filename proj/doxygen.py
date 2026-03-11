from .config_file import ProjectConfig
from typing import (
    Optional,
    TextIO,
    Mapping,
)
from . import subprocess_trace as subprocess

def run_doxygen(
    config: ProjectConfig,
    stdout: Optional[TextIO],
    stderr: Optional[TextIO],
    env: Mapping[str, str],
) -> bool:
    assert config.doxygen_enabled

    env = {
        **env,
        "FF_HOME": str(config.base),
    }

    config.doxygen_dir.mkdir(exist_ok=True, parents=True)
    stdout_contents, stderr_contents = subprocess.tee_output_str(
        "doxygen docs/doxygen/Doxyfile 2>&1 | grep -v DOT_GRAPH_MAX_NODES",
        env=env,
        stdout=stdout,
        stderr=stderr,
        cwd=config.base,
        shell=True,
        check=False,
    )

    return len(stdout_contents.strip()) == 0 and len(stderr_contents.strip()) == 0
