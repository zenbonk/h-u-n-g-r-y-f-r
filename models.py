# -*- coding: utf-8 -*-
from mongoengine import *

from flask.ext.mongoengine.wtf import model_form
from datetime import datetime

# our demo model from week 5 in class
class Log(Document):
	text = StringField()
	timestamp = DateTimeField(default=datetime.now())

class Comment(EmbeddedDocument):
	name = StringField()
	comment = StringField()
	timestamp = DateTimeField(default=datetime.now())

class Idea(Document):

	creator = StringField(max_length=120, required=True, verbose_name="Hi my name is ")
	title = StringField(max_length=120, required=True, verbose_name=" and I'm hungryfr ")
	slug = StringField()
	idea = StringField(max_length=120, required=False, verbose_name="meet me in (hh:mm am/pm) ")
	duration = StringField(choices = (('a quick break','a quick break'),('not too long','not too long'), ('get me out of here!','get me out of here!')), verbose_name=" minutes for ")
	#duration = StringField(max_length=120, required=True, verbose_name="minutes, it'll take ")
	timeHour = StringField(max_length=120, required=False)
	timeHour2 = StringField(choices = (('5','5'),('10','10'),('15','15'),('20','20'), ('25','25'), ('30','30'), ('35','35'), ('40','40'), ('45','45'), ('50','50'), ('55','55'), ('60','60')) , verbose_name="meet me in ")
	timeMinute = StringField(max_length=120, required=False)
	timeAmPm = StringField(max_length=120, required=False)
	
	# current time
	idea.currentTime = DateTimeField(default=datetime.now())
	currentTime = DateTimeField(default=datetime.now())

	# Category is a list of Strings
	categories = ListField(StringField(max_length=30))

	# Comments is a list of Document type 'Comments' defined above
	comments = ListField( EmbeddedDocumentField(Comment) )

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())
	minutesRemaining = DateTimeField()
	deadline = DateTimeField()
	# now = DateTimeField()
	sms_sent = BooleanField(default=False)


# class TimeDisplay(Document):
	
# 	# current time
# 	#time.currentTimeDisplay = DateTimeField(default=datetime.now())
# 	currentTimeDisplay = DateTimeField(default=datetime.now())

# 	# Timestamp will record the date and time idea was created.
# 	timestampDisplay = DateTimeField(default=datetime.now())

# 	deadline = DateTimeField()

#[('01','02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'),('01','02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')], verbose_name = "Time",)
	

# Create a Validation Form from the Idea model
IdeaForm = model_form(Idea)

	

