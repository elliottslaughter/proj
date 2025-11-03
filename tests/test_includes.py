import pytest

from proj.includes import (
    get_include_path,
    get_generated_include_path,
    get_file_for_include_path,
    find_include_specs_in_cpp_file_contents,
    find_includes_in_cpp_file_contents,
    replace_include_in_cpp_file_contents,
    replace_include_in_dtg_toml_file_contents,
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
        
    result = find_include_specs_in_cpp_file_contents(file_contents, header_extension='.h')

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
