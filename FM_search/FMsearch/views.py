from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from FMsearch.models import refString, letterDetails

from . import FM
def index(request):
	resp={}
	resp['saved_refs'] = refString.objects.all()
	resp['formatted'] = ''
	resp['refString']=''
	if request.method == 'POST':
		#process a search submission
		if 'search' in request.POST:
			ref = request.POST['choice'].split(';')[0]
			query = request.POST['query']

			if query == '' or ref == 'none':
				resp['query_error'] = 'Choose a reference string and enter a query'
				return render(request, 'FMsearch/index.html',resp)
			
			word = refString.objects.get(pk=ref)
			
			occs = {}
			locs = {}
			totals = {}
			SA=[]
			#rebuild FM Index from stored data
			alph = word.letterdetails_set.all()
			for c in alph:
				occs[c.letter] = list(map(int,c.occ_data.split(',')))
				locs[c.letter] = int(c.c_data)
				totals[c.letter] = int(c.total)
			str_SA = word.SA.split(',')
			SA = list(map(int,str_SA))
			index = FM.FMIndex(word.data,c=locs,occ=occs,SA=SA,totals=totals)

			#search for query
			occ,loc = index.search(query)

			#create string showing search hits
			formatted=word.data
			size = len(query)
			loc = sorted(loc)
			offset=0
			if (loc != [-1]):
				for i in sorted(loc):
					i += offset
					formatted = formatted[0:i]+'['+formatted[i:i+size]+']'+formatted[i+size:]
					offset += 2
			
			#create formatted response
			locations = ''
			for i in loc:
				locations += str(i)+', '
			locations=locations[:-2]
			resp['formatted'] = formatted
			resp['response'] = ('%s occurence(s) at indexes: ' % str(occ) + locations )
			resp['refstring'] = word.data
			resp['query'] = query
			return render(request, 'FMsearch/index.html',resp)

		#create and store new FM Index
		if 'preprocess' in request.POST:
			name = request.POST['new_ref_name']
			new_ref = request.POST['new_ref']
			if name == '' or new_ref == '':
				resp['pre_error'] = 'Enter a name and reference string'
				return render(request, 'FMsearch/index.html',resp)
			
			newFM = FM.FMIndex(new_ref+'$')
			SA = ','.join(map(str,newFM.SA))
			new_refString = refString(name=name, data=new_ref, save_date=timezone.now(),SA=SA)
			new_refString.save()
			for c in newFM.occ.keys():
				new_refString.letterdetails_set.create(letter = c, occ_data=','.join(map(str,newFM.occ[c])),c_data=newFM.c[c],total=newFM.totals[c])

			resp['saved_refs'] = refString.objects.all()

			return render(request, 'FMsearch/index.html',resp)
	else:
		return render(request, 'FMsearch/index.html',resp)

# # Create your views here.
