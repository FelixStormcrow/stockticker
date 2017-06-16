from flask import Flask, render_template, request, redirect
import pandas as pd
import datetime as dt  
import dateutil.parser as parser
import bokeh.plotting as plt
from bokeh.resources import CDN
from bokeh.embed import components


app = Flask(__name__)

data_n=['open','close','adj_open','adj_close']
app.inputvars={}

for key in data_n:
	app.inputvars[key]='0'
app.inputvars['time_interval']='0'
app.inputvars['startdate']='0'
app.inputvars['enddate']='0'
app.inputvars['ticker']='AAPL'

def compute(dic,ticker):
        t=dic['time']
        p = plt.figure(title='Stock data for'+ticker,x_axis_label='time',y_axis_label='price',x_axis_type="datetime")
        data_n=['open','close','adj_open','adj_close']
        col=['black','blue','red','green']
        i=0
        for key in data_n:
                if key in dic.keys():
                        p.line(t,dic[key],legend=key,line_color=col[i], line_width=2)
                        i+=1
        p.legend.location='top_left'
        from bokeh.resources import CDN
        from bokeh.embed import components
        script, div = components(p)
        head = """
<link rel="stylesheet"
 href="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.css"
 type="text/css" />
<script
 src="http://cdn.pydata.org/bokeh/release/bokeh-0.9.0.min.js">
</script>
"""
        return head, script, div

def assemble_string():
	str_base='https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?ticker='  
	str_col='&qopts.columns=date'
	for key in data_n:
		if app.inputvars[key] == '1': str_col=str_col+','+key
	str_api='&api_key=cfG6Lxrn_4Pg8J8jLodw'
	ticker=app.inputvars['ticker']
        str_time=assemble_time(app.inputvars['time_interval'],app.inputvars['startdate'],app.inputvars['enddate'])
        return str_base+ticker+str_col+str_time+str_api

def assemble_time(cat, start, end):
	if cat != '-1':
		end_date=dt.date.today()
		start_date=end_date-pd.tseries.offsets.DateOffset(months=int(cat))
        else:
                end_date=parser.parse(end)
                start_date=parser.parse(start)
        return '&date.gte='+start_date.strftime('%Y%m%d')+'&date.lte='+end_date.strftime('%Y%m%d')
		


@app.route('/',methods=['GET','POST'])
def main():
	return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def init_get_info():
	return render_template('index.html')

@app.route('/figure',methods=['POST'])
def proc_get_info():
	for key in app.inputvars:
		if key in request.form:
			app.inputvars[key]=request.form[key]
		else:
			app.inputvars[key]='0'
	
	if sum([int(app.inputvars[key]) for key in data_n])==0:
		return render_template('error.html',err='No data requested!')	


	assembled_string=assemble_string()
        f = open('quandl_string.txt','w')
	f.write(assembled_string)
	f.close()
	df = pd.read_json(assembled_string)
	data= df['datatable']['data']
	
	if len(data)==0:
		#no data, probably bad ticker
		return render_template('error.html',err='Data empty, might be a bad ticker!')

	columns={}
	for i, column in enumerate(df['datatable']['columns']):
		columns[column['name']]=i
	

	data_dic={}	
	dd = [dat[columns['date']] for dat in data]
	data_dic['time'] = [d.date() for d in pd.to_datetime(dd)]
	
	for key in data_n:
		if app.inputvars[key]=='1': data_dic[key]=[dat[columns[key]] for dat in data]

	result=compute(data_dic,app.inputvars['ticker'])

  	return render_template('figure.html', result=result)



if __name__ == '__main__':
    app.run(port=33507)
