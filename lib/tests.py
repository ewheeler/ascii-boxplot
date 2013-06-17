import nose
#import difflib
#from pprint import pprint

import boxplot


def test_multiple_series_and_name_generation():
    expected =\
"""          |-2.68333                                                 4.2|
 test data   -------------========0========-------------
  series-2                --------========0=========-------------
  series-3                        ------------=====0====--------------->"""

    result = boxplot.render([
        ("test data", [-2.5, -1, 0, 1, 2.5]),
        ("", [-1, 0, 1, 2, 3.5]),
        ("", [0, 1.5, 2, 2.5, 5.5]),
    ])
    assert result == expected


def test_box_weight():
    expected_1 =\
"""          |-2                                                         2|
 test data <--------------===============0===============-------------->"""

    expected_05 =\
"""          |-3                                                         3|
 test data      ---------------==========0==========---------------"""

    result_1 = boxplot.render([('test data', [-2.5, -1, 0, 1, 2.5])])
    #diff = difflib.Differ().compare(expected_1.splitlines(1), result_1.splitlines(1))
    #pprint(list(diff))
    assert result_1 == expected_1

    result_05 = boxplot.render([('test data', [-2.5, -1, 0, 1, 2.5])], box_weight=0.5)
    assert result_05 == expected_05


if __name__ == '__main__':
    nose.main()
