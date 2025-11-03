from proj.ifndef import (
    set_ifndef,
    get_current_ifndef,
)
import textwrap

def test_get_ifndef() -> None:
    content = '''
        // something
        // unrelated
         #ifndef MY_IFNDEF
           #define MY_IFNDEF

        other
        stuff

         #endif // MY_IFNDEF

        trailing
        stuff
    '''
    
    result = get_current_ifndef(content)
    correct = 'MY_IFNDEF'

    assert result == correct

def test_get_ifndef_for_simple() -> None:
    content = textwrap.dedent('''
    #ifndef _LIB2_INCLUDE_LIB2_H
    #define _LIB2_INCLUDE_LIB2_H

    namespace TestProject {

    void call_lib2();

    }

    #endif
    ''').strip() + '\n'
    
    result = get_current_ifndef(content)
    correct = '_LIB2_INCLUDE_LIB2_H'

    assert result == correct


def test_set_ifndef() -> None:
    content = '''
        // something
        // unrelated
         #ifndef MY_IFNDEF
           #define MY_IFNDEF

        other
        stuff

         #endif // MY_IFNDEF

        trailing
        stuff
    '''
    
    result = set_ifndef(content, 'MY_OTHER_IFNDEF')

    correct = '''
        // something
        // unrelated
         #ifndef MY_OTHER_IFNDEF
           #define MY_OTHER_IFNDEF

        other
        stuff

         #endif // MY_OTHER_IFNDEF

        trailing
        stuff
    '''

    assert result == correct
