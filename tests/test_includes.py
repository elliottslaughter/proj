import pytest

from proj.includes import (
    get_include_path,
    get_generated_include_path,
    get_file_for_include_path,
    find_include_specs_in_cpp_file_contents,
    find_includes_in_cpp_file_contents,
    replace_include_in_cpp_file_contents,
    replace_include_in_dtg_toml_file_contents,
    find_includes_in_dtgen_toml_file_contents,
    find_occurrences_of_include,
    IncludeSpec,
    UnknownInclude,
    SystemInclude,
)
from proj.paths import (
    FileGroup,
    Library,
)
from pathlib import PurePath
from typing import (
    Optional,
)
from proj.trees import EmulatedFileTree
from proj.config_file import ExtensionConfig

def test_get_include_path() -> None:
    file_group = FileGroup(
        PurePath('a/b'),
        Library('c'),
    )

    result = get_include_path(
        file_group, 
        header_extension='.hhh',
    )

    correct = PurePath('c/a/b.hhh')

    assert result == correct

def test_get_generated_include_path() -> None:
    file_group = FileGroup(
        PurePath('a/b'),
        Library('c'),
    )

    result = get_generated_include_path(
        file_group, 
        header_extension='.hhh',
    )

    correct = PurePath('c/a/b.dtg.hhh')

    assert result == correct


@pytest.mark.parametrize("include_path,correct", [
    (
        PurePath('c/a/b.hhh'),
        FileGroup(PurePath('a/b'), Library('c')).public_header,
    ),
    (
        PurePath('c/a/b.dtg.hhh'),
        FileGroup(PurePath('a/b'), Library('c')).generated_header,
    ),
    (
        PurePath('c/a/b.h'),
        None,
    ),
    (
        PurePath('c/a/b'),
        None,
    ),
    (
        PurePath('c.hhh'),
        None,
    ),
])
def test_get_file_for_include_path(include_path: PurePath, correct: Optional[FileGroup]) -> None:
    result = get_file_for_include_path(include_path, header_extension='.hhh')

    assert result == correct

def test_find_includes_in_cpp_file_contents() -> None:
    file_contents = '''
        // something
        // unrelated
         #ifndef MY_OTHER_IFNDEF
           #define MY_OTHER_IFNDEF

        #include "something/else.h"
        #include "fmt/format.hh"
            #include <something/format.h>
          #include "something/else.dtg.h"
        #include <fmt/format.h>

        other
        stuff

        #include "a/b/c.h"
         #endif // MY_OTHER_IFNDEF

        trailing
        stuff
    '''
        
    result = find_includes_in_cpp_file_contents(
        file_contents, 
        header_extension='.h',
    )

    correct = [
        FileGroup(PurePath('else'), Library('something')).public_header,
        UnknownInclude(PurePath('fmt/format.hh')),
        SystemInclude(PurePath('something/format.h')),
        FileGroup(PurePath('else'), Library('something')).generated_header,
        SystemInclude(PurePath('fmt/format.h')),
        FileGroup(PurePath('b/c'), Library('a')).public_header,
    ]

    assert result == correct


def test_find_include_specs_in_cpp_file_contents() -> None:
    file_contents = '''
        // something
        // unrelated
         #ifndef MY_OTHER_IFNDEF
           #define MY_OTHER_IFNDEF

        #include "something/else.h"
        #include "fmt/format.hh"
            #include <something/format.h>
          #include "something/else.dtg.h"
        #include <fmt/format.h>

        other
        stuff

        #include "a/b/c.h"
         #endif // MY_OTHER_IFNDEF

        trailing
        stuff
    '''
        
    result = find_include_specs_in_cpp_file_contents(file_contents)

    correct = [
        IncludeSpec(PurePath('something/else.h'), system=False),
        IncludeSpec(PurePath('fmt/format.hh'), system=False),
        IncludeSpec(PurePath('something/format.h'), system=True),
        IncludeSpec(PurePath('something/else.dtg.h'), system=False),
        IncludeSpec(PurePath('fmt/format.h'), system=True),
        IncludeSpec(PurePath('a/b/c.h'), system=False),
    ]

    assert result == correct

def test_replace_include_in_cpp_file_contents():
    file_contents = '''
        // something
        // unrelated
         #ifndef MY_OTHER_IFNDEF
           #define MY_OTHER_IFNDEF

        #include "something/else.h"
        #include "fmt/format.hh"
            #include <something/format.h>
          #include "something/else.dtg.h"
         #include   <fmt/format.h>

        other
        stuff

        #include "a/b/c.h"
         #endif // MY_OTHER_IFNDEF

        trailing
        stuff
    '''

    result = replace_include_in_cpp_file_contents(file_contents, PurePath('fmt/format.h'), PurePath('other/path/thing.hh'))

    correct = '''
        // something
        // unrelated
         #ifndef MY_OTHER_IFNDEF
           #define MY_OTHER_IFNDEF

        #include "something/else.h"
        #include "fmt/format.hh"
            #include <something/format.h>
          #include "something/else.dtg.h"
         #include   <other/path/thing.hh>

        other
        stuff

        #include "a/b/c.h"
         #endif // MY_OTHER_IFNDEF

        trailing
        stuff
    '''

    assert result == correct

def test_find_include_specs_in_dtgen_toml_file_contents() -> None:
    file_contents = '''
        namespace = "FlexFlow"
        name = "MyList"
        type = "variant"
        features = [
          "eq",
          "ord",
          "hash",
          "json",
          "fmt",
        ]

        template_params = [
          "T",
        ]

        includes = [
          "person/my_list_cons.dtg.hh",
        ]

        src_includes = [
          "<unordered_set>",
          "person/my_list_empty.dtg.hh",
          "something_else_entirely.hh",
        ]

        [[values]]
        type = "::FlexFlow::MyListCons<T>"
        key = "cons"

        [[values]]
        type = "::FlexFlow::MyListEmpty"
        key = "empty"
    '''

    result = list(find_includes_in_dtgen_toml_file_contents(file_contents, header_extension='.hh'))

    correct = [
        FileGroup(PurePath("my_list_cons"), Library("person")).generated_header,
        SystemInclude(PurePath("unordered_set")),
        FileGroup(PurePath("my_list_empty"), Library("person")).generated_header,
        UnknownInclude(PurePath("something_else_entirely.hh")),
    ]
    
    assert result == correct

def test_replace_include_in_dtg_toml_file_contents() -> None:
    file_contents = '''
        namespace = "FlexFlow"
        name = "MyList"
        type = "variant"
        features = [
          "eq",
          "ord",
          "hash",
          "json",
          "fmt",
        ]

        template_params = [
          "T",
        ]

        includes = [
          "person/my_list_cons.dtg.hh",
          "person/my_list_empty.dtg.hh",
        ]

        [[values]]
        type = "::FlexFlow::MyListCons<T>"
        key = "cons"

        [[values]]
        type = "::FlexFlow::MyListEmpty"
        key = "empty"
    '''

    result = replace_include_in_dtg_toml_file_contents(
        file_contents, 
        curr=PurePath('person/my_list_cons.dtg.hh'),
        goal=PurePath('something/else/entirely.h'),
    )

    correct = '''
        namespace = "FlexFlow"
        name = "MyList"
        type = "variant"
        features = [
          "eq",
          "ord",
          "hash",
          "json",
          "fmt",
        ]

        template_params = [
          "T",
        ]

        includes = [
          "something/else/entirely.h",
          "person/my_list_empty.dtg.hh",
        ]

        [[values]]
        type = "::FlexFlow::MyListCons<T>"
        key = "cons"

        [[values]]
        type = "::FlexFlow::MyListEmpty"
        key = "empty"
    '''

    assert result == correct

def test_find_occurrences_of_include() -> None:
    matching_header_path = 'lib/example/include/example/something_else.h'
    matching_header_file = FileGroup(
        PurePath('something_else'),
        Library('example'),
    ).public_header
    matching_header_contents = '''
        #ifndef MY_OTHER_IFNDEF
        #define MY_OTHER_IFNDEF

        #include "find/me.h"
        #include "not/me.h"

        #endif // MY_OTHER_IFNDEF
    '''

    non_matching_header_path = 'lib/example/include/example/papayas.h'
    non_matching_header_contents = '''
        #ifndef MY_OTHER_IFNDEF
        #define MY_OTHER_IFNDEF

        #include "not/me.h"

        #endif // MY_OTHER_IFNDEF
    '''

    matching_toml_path = 'lib/example/include/example/integer.dtg.toml'
    matching_toml_file = FileGroup(
        PurePath('integer'),
        Library('example'),
    ).dtgen_toml
    matching_toml_contents = '''
        namespace = "FlexFlow"
        name = "MyList"
        type = "variant"
        features = []

        includes = [
          "find/me.h",
          "not/me.h",
        ]

        values = []
    '''

    non_matching_toml_path = 'lib/example/include/example/another_integer.dtg.toml'
    non_matching_toml_contents = '''
        namespace = "FlexFlow"
        name = "MyList"
        type = "variant"
        features = []

        includes = [
          "not/me.h",
        ]

        values = []
    '''


    repo_file_tree = EmulatedFileTree.from_lists(
        curr_time=10,
        files=[
            (
                matching_toml_path,
                1,
                matching_toml_contents,
            ),
            (
                matching_header_path,
                1,
                matching_header_contents,
            ),
            (
                non_matching_toml_path,
                1,
                non_matching_toml_contents,
            ),
            (
                non_matching_header_path,
                1,
                non_matching_header_contents,
            ),
        ],
        dirs=[]
    )

    to_find = IncludeSpec(
        PurePath('find/me.h'),
        system=False,
    )

    extension_config = ExtensionConfig(
        header_extension='.h',
        src_extension='.cc',
    )

    result = find_occurrences_of_include(
        repo_file_tree,  
        to_find,
        extension_config,
    )

    correct = {
        matching_header_file,
        matching_toml_file,
    }

    assert result == correct
