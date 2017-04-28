"""
List of HTML5 tags. Taken from: https://www.w3schools.com/Tags/
"""
from bricks.components.core import Tag, VoidTag


#
# Define HTML Tags
#
def tag(tag, help_text=None):
    """
    Return an HTMLTag subclass for the given tag.
    """

    # https://www.w3.org/TR/html5/syntax.html#void-elements
    void_elements = (
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen',
        'link', 'meta', 'param', 'source', 'track', 'wbr')
    cls = VoidTag if tag in void_elements else Tag
    ns = {'help_text': help_text}
    return type(tag, (cls,), ns)


#
# Basic document structure
#
HTML5 = document = tag('html', 'The root of an HTML document')
body = tag('body', "The document's body")
head = tag('head', 'Information about the document')

#
# Meta information (tags that appear under <head>
#
meta = tag('meta', 'Defines metadata about an HTML document')
link = tag('link', 'Relationship with and an external resource')
title = tag('title', 'A title for the document')

#
# Generic tags
#
div = tag('div', 'A section in a document (block)')
span = tag('span', 'A section in a document (text)')

#
# Structural tags
#
article = tag('article', 'An article')
aside = tag('aside', 'Content aside from the page content')
details = tag('details', 'Details that the user can view or hide')
footer = tag('footer', 'A footer for a document or section')
figcaption = tag('figcaption', 'A caption for a <figure> element')
figure = tag('figure', 'Specifies self-contained content')
header = tag('header', 'A header for a document or section')
main = tag('main', 'Specifies the main content of a document')
p = tag('p', 'A paragraph')
pre = tag('pre', 'Preformatted text')
section = tag('section', 'A section in a document')

# ------------------------------------------------------------------------------
# The following sections are in alphabetical order

#
# External elements
#
embed = tag('embed', 'A container for an external (non-HTML) application')
iframe = tag('iframe', 'An inline frame')
noscript = tag('noscript', 'Content for users that do not support scripts')
object = tag('object', 'An embedded object')
script = tag('script', 'A client-side script')
style = tag('style', 'Defines style information for a document')

#
# Forms
#
button = tag('button', 'A clickable button')
fieldset = tag('fieldset', 'Groups related elements in a form')
form = tag('form', 'An HTML form for user input')
input = tag('input', 'An input control')
keygen = tag('keygen', 'A key-pair generator field')
label = tag('label', 'A label for an <input> element')
legend = tag('legend', 'A caption for a <fieldset> element')
optgroup = tag('optgroup', "A group of related <option>'s")
option = tag('option', 'An option in a drop-down list')
select = tag('select', 'A drop-down list')
textarea = tag('textarea', 'A multiline input control')

#
# Headings
#
h1 = tag('h1', 'Defines HTML heading')
h2 = tag('h2', 'Defines HTML heading')
h3 = tag('h3', 'Defines HTML heading')
h4 = tag('h4', 'Defines HTML heading')
h5 = tag('h5', 'Defines HTML heading')
h6 = tag('h6', 'Defines HTML heading')

#
# Lists/description lists
#
dd = tag('dd', 'A value of a term in a description list')
dl = tag('dl', 'A description list')
dt = tag('dt', 'A term/name in a description list')
ul = tag('ul', 'An unordered list')
li = tag('li', 'A list item')
ol = tag('ol', 'An ordered list')

#
# Multimedia and images
#
area = tag('area', 'An area inside an image-map')
audio = tag('audio', 'Defines sound content')
canvas = tag('canvas', 'Draw graphics via scripting')
img = tag('img', 'An image')
picture = tag('picture', 'A container for multiple image resources')
track = tag('track', 'Text tracks for media elements (<video> and <audio>)')
video = tag('video', 'A video or movie')
source = tag('source', 'Media resources for video/audio elements')

#
# Navigation
#
a = tag('a', 'A hyperlink')
menu = tag('menu', 'A list/menu of commands')
menuitem = tag('menuitem', 'An item on a popup menu')
nav = tag('nav', 'Defines navigation links')

#
# Roles
#
abbr = tag('abbr', 'An abbreviation or an acronym')
blockquote = tag('blockquote', 'Section quoted from another source')
code = tag('code', 'A piece of computer code')

#
# Tables
#
caption = tag('caption', 'A table caption')
col = tag('col', 'Specifies a column within a <colgroup>')
colgroup = tag('colgroup', 'Group of columns in a table')
table = tag('table', 'A table')
tbody = tag('tbody', 'Groups the body content in a table')
td = tag('td', 'A cell in a table')
tfoot = tag('tfoot', 'Groups the footer content in a table')
th = tag('th', 'A header cell in a table')
thead = tag('thead', 'Groups the header content in a table')
tr = tag('tr', 'A row in a table')

#
# Text roles and styling
#
b = tag('b', 'Bold text')
em = tag('em', 'Emphasized text')
del_ = tag('del', 'Text that has been deleted from a document')
i = tag('i', 'A part of text in an alternate voice or mood')
ins = tag('ins', 'A text that has been inserted into a document')
mark = tag('mark', 'Defines marked/highlighted text')
q = tag('q', 'A short quotation')
s = tag('s', 'Text that is no longer correct')
small = tag('small', 'Defines smaller text')
strong = tag('strong', 'Important text')
sub = tag('sub', 'Subscripted text')
sup = tag('sup', 'Superscripted text')
u = tag('u', 'Marks stylistically different text')

#
# Textual breaks
#
br = tag('br', 'A single line break')
hr = tag('hr', 'A thematic change in the content')
wbr = tag('wbr', 'A possible line-break')

#
# Typographical and text annotations for different languages
#
bdi = tag('bdi', 'Isolates text with a possible different direction')
bdo = tag('bdo', 'Overrides the current text direction')
rp = tag('rp', 'Display text for browsers that do not support ruby annotations')
rt = tag('rt', 'Explanation/pronunciation of characters')
ruby = tag('ruby', 'A ruby annotation (for East Asian typography)')

# ------------------------------------------------------------------------------
# Uncategorized tags
#
address = tag('address',
              'Defines contact information for the author/owner of a document')
dialog = tag('dialog', 'A dialog box or window')
base = tag('base',
           'Specifies the base URL/target for all relative URLs in a document')
cite = tag('cite', 'The title of a work')
datalist = tag('datalist',
               'Specifies a list of pre-defined options for input controls')
dfn = tag('dfn', 'Represents the defining instance of a term')
kbd = tag('kbd', 'Defines keyboard input')
map = tag('map', 'A client-side image-map')
meter = tag('meter', 'A scalar measurement within a known range (a gauge)')
param = tag('param', 'A parameter for an object')
progress = tag('progress', 'Represents the progress of a task')
samp = tag('samp', 'Defines sample output from a computer program')
summary = tag('summary', 'A visible heading for a <details> element')
time = tag('time', 'A date/time')
var = tag('var', 'A variable')
output = tag('output', 'The result of a calculation')

# ------------------------------------------------------------------------------
# List of deprecated tags.
#
# We keep them here in case we ever want to support HTML4.
# In case you are wondering, this is a *very low* priority.
#
# <acronym>	Not supported in HTML5. Use <abbr> instead. An acronym
# <applet>	Not supported in HTML5. Use <embed> or <object> instead. An embedded applet
# <big>	Not supported in HTML5. Use CSS instead. Defines big text
# <basefont>	Not supported in HTML5. Use CSS instead. Specifies a default color, size, and font for all text in a document
# <center>	Not supported in HTML5. Use CSS instead.Defines centered text
# <dir>	Not supported in HTML5. Use <ul> instead. A directory list
# <font>	Not supported in HTML5. Use CSS instead. Defines font, color, and size for text
# <frame>	Not supported in HTML5. A window (a frame) in a frameset
# <frameset>	Not supported in HTML5. A set of frames
# <noframes>	Not supported in HTML5. An alternate content for users that do not support frames
# <strike>	Not supported in HTML5. Use <del> or <s> instead. Defines strikethrough text
# <tt>	Not supported in HTML5. Use CSS instead. Teletype text
#

del tag
