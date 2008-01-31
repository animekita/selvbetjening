from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import units

users = [] # contains utf strings u'username firstname lastname' or (u'username firstname lastname', usernameSize, nameSize)

def drawCard(canvas, x, y, name, alias, usernameSize, nameSize):
    elements = []
    elements.append(Image('idkort.jpg', units.toLength('75mm'), units.toLength('40mm')))

    frame = Frame(x, y, 75 * units.mm, 40 * units.mm, showBoundary=0, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
    frame.addFromList(elements, canvas)

    canvas.setFont('Howie_s_Funhouse', nameSize)
    canvas.drawString(x + 21 * units.mm, y + 15 * units.mm, name)

    canvas.setFont('Howie_s_Funhouse', usernameSize)
    canvas.drawString(x + 21 * units.mm, y + 4 * units.mm, alias)

def format_name(name):
    names = name.rstrip().title().split(' ')
    return names[0] + ' ' + names[len(names)-1]

pdfmetrics.registerFont(TTFont('Howie_s_Funhouse', 'Howie_s_Funhouse.ttf'))

i = 0

while i < len(users):
    canvas = Canvas('idkort%s.pdf' % i)
    canvas.setFont('Howie_s_Funhouse', 16)
    for column in range(2):
        for row in range(6):
	     if i < len(users):
		 if isinstance(users[i], tuple):
                     user = users[i][0].split(' ', 1)
                     usernameSize = users[i][1]
                     nameSize = users[i][2]
                 else:
		     user = users[i].split(' ', 1)
                     usernameSize = 16
                     nameSize = 16

                 drawCard(canvas, 30 * units.mm + column * 75 * units.mm, 30 * units.mm + row * 40 * units.mm, format_name(user[1][:-1]), user[0], usernameSize, nameSize)
	     else:
                 drawCard(canvas, 30 * units.mm + column * 75 * units.mm, 30 * units.mm + row * 40 * units.mm, '', '', usernameSize, nameSize)
		
	     i = i + 1
    canvas.save()
