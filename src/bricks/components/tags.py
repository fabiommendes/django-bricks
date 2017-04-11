from bricks.components.core import Tag


#
# Define HTML Tags
#
def tag_factory(tag):
    """
    Return an HTMLTag subclass for the given tag.
    """

    return type(tag, (Tag,), {'_tag_name': tag})


# Generic tags
div = tag_factory('div')
span = tag_factory('span')

# Content tags
nav = tag_factory('nav')

# Meta tags
meta = tag_factory('meta')
link = tag_factory('link')
script = tag_factory('script')
head = tag_factory('head')
title = tag_factory('title')
body = tag_factory('body')
document = tag_factory('html')

# Lists
ul = tag_factory('ul')
ol = tag_factory('ol')
li = tag_factory('li')

# Text
p = tag_factory('p')
a = tag_factory('a')
br = tag_factory('br')

# Headings
h1 = tag_factory('h1')
h2 = tag_factory('h2')
h3 = tag_factory('h3')
h4 = tag_factory('h4')
h5 = tag_factory('h5')
h6 = tag_factory('h6')
