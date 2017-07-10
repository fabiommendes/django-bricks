from bricks.html5 import div, p, button, span, h1
from bricks.queries import query


elements = div(class_="a") [
    p(class_="b") [
        button(onclick="alert(123)", class_="c") [ "click" ],
    ],

    div() [
        p(class_="c") [ "so texto" ]
    ],

    span(class_="b") [
        "text aqui",

        h1(style="color:blue", onmousehover="alert(456)") [
            "Eta !"
        ]
    ],

    p(class_="b", style="color:red") [
        "Hello hello hello",
        h1() [
            "Melhora do jeito que achar melhor"
        ]
    ]
]


def test_with_class_attr():
    res = query(elements, class_='b')
    assert len(res) == 3
    assert ['b' in x.classes for x in res]

    res = query(elements, class_='c')
    assert len(res) == 2
    assert ['c' in x.classes for x in res]


def test_with_tag_attr():
    res = query(elements, tag='p')
    assert len(res) == 3
    assert ['p' in x.tag_name for x in res]

    res = query(elements, tag='h1')
    assert len(res) == 2
    assert ['h1' in x.tag_name for x in res]


def test_with_other_attrs():
    res = query(elements, onclick='alert(123)')
    assert len(res) == 1
    assert ['onclick' in x.attrs for x in res]

    res = query(elements, style='color:red')
    assert len(res) == 1
    assert ['style' in x.attrs for x in res]


def test_with_more_than_one_attrs():
    res = query(elements, style="color:blue", onmousehover="alert(456)")
    assert len(res) == 1
    assert ['h1' in x.tag_name for x in res]
