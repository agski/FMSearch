from django.db import models

# Create your models here.
class refString(models.Model):
	name = models.CharField(max_length=50)
	data = models.CharField(max_length=1000)
	save_date = models.DateTimeField('date created')
	SA = models.CharField(max_length=1000)

	def __str__(self):
		return self.data

class letterDetails(models.Model):
	refString = models.ForeignKey(refString, on_delete=models.CASCADE)
	letter = models.CharField(max_length=1)
	occ_data = models.CharField(max_length=1000)
	c_data = models.IntegerField()
	total = models.IntegerField()

	def __str__(self):
		return (self.letter, self.occ_data, self.c_data, self.total)

