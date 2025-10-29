# from .path_tree import (
#     PathTree,
# )
# from pathlib import (
#     PurePath,
# )
# import logging
# from typing import (
#     Optional,
# )
# from dataclasses import dataclass
# from .paths import (
#     Library,
# )
#
# _l = logging.getLogger(__name__)
#
# def get_sublib_root(repo_path_tree: PathTree, p: PurePath) -> Optional[PurePath]:
#     while True:
#         assert repo_path_tree.has_path(p)
#
#         src_dir = p / "src"
#         include_dir = p / "include"
#
#         src_exists = repo_path_tree.has_dir(src_dir)
#         include_exists = repo_path_tree.has_dir(include_dir)
#
#         _l.debug(
#             "get_sublib_root checking %s for %s is dir (%s) and %s is dir (%s)",
#             p,
#             src_dir,
#             src_exists,
#             include_dir,
#             include_exists,
#         )
#
#         if src_exists and include_exists:
#             return p
#
#         if p == p.parent:
#             return None
#         else:
#             p = p.parent
#
#
# @dataclass(frozen=True, order=True)
# class LibAttrs:
#     has_test_dir: bool
#     has_benchmark_dir: bool
#
# @dataclass(frozen=True, order=True)
# class LibInfo:
#     library: Library
#     attrs: LibAttrs
#
# def get_library_id(repo_path_tree: PathTree, p: PurePath) -> Library:
#     assert repo_path_tree.has_path(p)
#     sublib_root = get_sublib_root(repo_path_tree, p)
#     assert sublib_root is not None
#     return Library(sublib_root.name)
#
# # def get_lib_info(repo_path_tree: PathTree, p: PurePath) -> LibInfo:
# #     assert repo_path_tree.has_path(p)
# #
# #     library = get_library_id(repo_path_tree, p)
# #
# #     sublib_root = get_sublib_root(repo_path_tree, p)
# #     assert sublib_root is not None
# #
# #     include_dir = sublib_root / "include"
# #     assert repo_path_tree.has_dir(include_dir)
# #
# #     src_dir = sublib_root / "src"
# #     assert repo_path_tree.has_dir(src_dir)
# #
# #     test_dir = sublib_root / "test"
# #     rel_test_dir: Optional[PurePath]
# #     if repo_path_tree.has_dir(test_dir):
# #         rel_test_dir = test_dir
# #     else:
# #         rel_test_dir = None
# #
# #     benchmark_dir = sublib_root / "benchmark"
# #     rel_benchmark_dir: Optional[PurePath]
# #     if repo_path_tree.has_dir(benchmark_dir):
# #         rel_benchmark_dir = benchmark_dir
# #     else:
# #         rel_benchmark_dir = None
# #
# #     return LibInfo(
# #         include_dir=include_dir,
# #         src_dir=src_dir,
# #         test_dir=rel_test_dir,
# #         benchmark_dir=rel_benchmark_dir,
# #     )
#
# # def with_project_specific_extension_removed(p: Path, config: ProjectConfig) -> Path:
# #     project_specific = [
# #         ".struct.toml",
# #         ".variant.toml",
# #         ".enum.toml",
# #         ".dtg" + config.header_extension,
# #         ".dtg.cc",
# #         ".test.cc",
# #         ".cc",
# #         ".cu",
# #         ".cpp",
# #         config.header_extension,
# #     ]
# #
# #     suffixes = "".join(p.suffixes)
# #
# #     for extension in project_specific:
# #         if suffixes.endswith(extension):
# #             return with_suffixes(p, suffixes[: -len(extension)])
# #
# #     raise ValueError(f"Could not find project-specific extension for path {p}")
# #
