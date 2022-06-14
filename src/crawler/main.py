from datetime import datetime, timedelta
import chinatimes, cna, ettoday, ftv, setn, storm, tvbs
from multiprocessing import Pool


def run_crawler(f, start_datetime, end_datetime):
    for _ in range(3):
        try:
            f(start_datetime, end_datetime)
            break
        except:
            pass
    return


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_end_date',
                    help='enter input end date')

    parser.add_argument('--input_start_date',
                    help='enter input start date')

    args = parser.parse_args()
    end_date =  args.input_end_date
    start_date = args.input_start_date

    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    end_datetime = datetime.combine(end_date, datetime.min.time())
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    start_datetime = datetime.combine(start_date, datetime.min.time())
    # today =  datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # end_datetime = today - timedelta(days=1)
    # start_datetime = today - timedelta(days=2)


    crawler_list = [ cna.crawler, ettoday.crawler, chinatimes.crawler,ftv.crawler, setn.crawler, storm.crawler] # , tvbs.crawler ] # chinatimes.crawler, chinatimes , ettoday.crawler only one day ; cna.crawler, # only two days
    items = [(f, start_datetime, end_datetime) for f in crawler_list]


    with Pool(len(crawler_list)) as p:
        p.starmap(run_crawler, items)



