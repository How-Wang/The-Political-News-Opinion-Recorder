#-*- coding: utf-8 -*-
from pathlib import Path
from flask import Flask, render_template, send_from_directory, url_for,redirect
import json
import csv
import pandas as pd
import sys
from datetime import datetime, timedelta, date

from sklearn import cluster


sys.path.insert(0, '..')
from opinion.extract.v0.v0_run import *
app = Flask(__name__)
# app.run(threaded=True)


# run code in certain time test ==================================
def sensor():
    """ Function for test purposes. """
    print("Scheduler is alive!")

def opinion_extraction():#end_datetime, start_datetime):

    end_datetime = date(2022, 6, 13)#.replace(hour=0, minute=0, second=0, microsecond=0) 
    start_datetime  = end_datetime- timedelta(days=1)
    
    # 1. take the crwaler result
    # 2. do extraction
    run_extraction(end_datetime, start_datetime)
    # 3. change structure to fit UI
    # 4. save to gcp
    fit_UI_format()
    return 0

# from apscheduler.schedulers.background import BackgroundScheduler
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(sensor,trigger='cron', hour='1')
# sched.add_job(opinion_extraction,trigger='cron', hour='1')
# sched.add_job(sensor,trigger='interval', seconds=1)
# sched.add_job(opinion_extraction,trigger='cron', hour='1')
# sched.start()


# dynamic route =====================================================================
@app.route('/')
def test():
    # date = None
    #station = None
	return redirect(url_for('dynamic_page', date='2022-06-11', station='now'))

@app.route('/dynamic/page/<date>/<station>')
def dynamic_page(date, station):
    if station == 'last':
        date = datetime.strptime(date, '%Y-%m-%d').date() - timedelta(days=1)
    elif station == 'next':
        date = datetime.strptime(date, '%Y-%m-%d').date() + timedelta(days=1)
    file_path = "../crawler/result/fit_UI/" + str(date) + "-page-dataset/page-table.json"
    
    if Path(file_path).is_file():
        with open("../crawler/result/fit_UI/" + str(date) + "-page-dataset/page-table.json",encoding= "utf-8") as f:
            context = json.load(f)
        return render_template("dynamic_front.html",**context)
    else:
        return render_template("not_belong.html")

@app.route('/dynamic/page_datetime/<datetime>')
def dynamic_datetime_page(datetime):
    date = datetime.split()[0]
    file_path = "../crawler/result/fit_UI/" + date + "-page-dataset/page-table.json"
    with open(file_path,encoding= "utf-8") as f:
        context = json.load(f)
    return render_template("dynamic_front.html",**context)


@app.route('/dynamic/cluster/<date>/<topic>')
def dynamic_cluster(date, topic):
    with open("../crawler/result/fit_UI/" + str(date) + "-cluster-list-dataset/cluster-" + str(topic) +"-table.json",encoding= "utf-8") as f:
        context = json.load(f)
    return render_template("dynamic_list.html",**context)

@app.route('/dynamic/opinions/<date>/<index>')
def dynamic_opinions(date, index):
    with open("../crawler/result/fit_UI/" + str(date) + "-opinions-dataset/" + str(index) +"-table.json",encoding= "utf-8") as f:
        context = json.load(f)
        # context["opinions"] = json.load(context["opinions"].replace("'",'"'))
        context["opinions"] = sorted(json.loads(context["opinions"].replace("'", '"')),
                             key=lambda d: d['order'])
    return render_template("dynamic_opinions.html",**context)

@app.route('/dynamic/person/<name>/<date>/<little_cluster_number>')
def dynamic_person(name,date,little_cluster_number):
    cc_df = pd.read_csv("../opinion/extract/result/cluster_cluster_table.csv")
    total_cluster_number = -1
    # find out total cluster number
    for i in range(len(cc_df)):
        if date == cc_df.iloc[i]['date'] and little_cluster_number == str(cc_df.iloc[i]['little_cluster_number']):
            total_cluster_number = cc_df.iloc[i]['total_cluster_number']
            break
    file_path = "../crawler/result/fit_UI/person-sliced-dataset/" + str(name) + "-" + str(total_cluster_number) +".json"
    if Path(file_path).is_file():
        with open(file_path,encoding= "utf-8") as f:
            context = json.load(f)
        return render_template("dynamic_person.html",**context)
    else:
        return render_template("not_belong.html")

@app.route("/dynamic/pic/<name>", methods=["GET"])
def pic(name):
    name = name.encode("utf-8").decode("latin1").encode('iso-8859-1').decode('utf8')      
    return send_from_directory('../crawler/result/fit_UI/pic/', name)

@app.route("/dynamic/cluster_pic/<date>/<cluster>", methods=["GET"])
def cluster_pic(date, cluster):
    DIR_PATH = "../crawler/result/fit_UI/cluster_pic/" + date + "/"
    return send_from_directory(DIR_PATH, cluster)

# ===============================================================
if __name__ == '__main__':
    opinion_extraction()
    app.run('0.0.0.0', 5000)
