from bricks.html5 import div, p, button, query, span

def print_found(tags):
    for tag in tags:
        print(tag)

a = div(class_="a") [
    p(class_="b") [
        button(onclick="alert(123)", class_="e") [ "click" ]
    ],

    div() [
        p(class_="c") [ "so texto" ]
    ],

    span(class_="b") [
        "text aqui"
    ],

    p(class_="b") [
        "Hello hello hello"
    ]
]

def test_has_class_B():
    q = query(a, class_='b')
    assert q
    assert ['b' in x.classes for x in q]

print("="*80)
print("Has tag span")
print_found(
    query(a, tag="span")
)

print("="*80)
print("Has onclick attr")
print_found(
    query(a, onclick='alert(123)')
)

print("="*80)
print("Has class c")
print_found(
    query(a, class_='c')
)

print("="*80)
print("Has tag p and class b")
print_found(
    query(a, tag='p', class_='b')
)