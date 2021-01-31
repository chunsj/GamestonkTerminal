""" Example or something

    Is this not informative enough?

    Load a specific stock
    Then apply a specific TA on it

    Do this because AlphaVantage only allows 5 API calls per minutes.
    This way we only need 1 call, and can apply TA to the result without
    using an API request.

    Multiple TA with kind stock

    Do my own personal Fundamental Analysis Dataframe
    Do option to explain important key metrics

    Do own personal Technical Analysis with multiple indicators perhaps?

    Split Menu into fa, ta and pred. Fundamental Analysis, Technical Analysis and Prediction, respectively.

    Do Reddit popularity study! 
    - By using defined ticker
    - By looking for mentioned tickers
    - By giving your own subreddit, using used ones.

    At the end, provide save tool where we save all data into an excel with:

    NIO_datetimesaved.xlsx
    - Sheet1 - Profile/Overview (FMP or AV)
    - Sheet2 - Finance (Market watch)
    - Sheet3 - Earnings (Market watch)
    - Sheet4 - SEC filings
    - Sheet5 - Insiders
    - Sheet6 - Analyst prices
    - Sheet7 - News
    - Sheet8 - Warnings & Key metrics
    - Sheet9 - Reddit popularity

"""
import argparse
import pandas as pd
from stock_market_helper_funcs import *
from fundamental_analysis import fa_menu as fam
from technical_analysis import ta_menu as tam
from due_diligence import dd_menu as ddm
from discovery import disc_menu as dm

# delete this important when automatic loading tesla
#i.e. when program is done
import config_bot as cfg
from alpha_vantage.timeseries import TimeSeries

# ----------------------------------------------------- LOAD -----------------------------------------------------
def load(l_args, s_ticker, s_start, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='load', description=""" Load a stock in order to perform analysis""")
    parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help="Stock ticker")
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date", help="The starting date (format YYYY-MM-DD) of the stock")
    parser.add_argument('-i', "--interval", action="store", dest="n_interval", type=int, default=1440, choices=[1,5,15,30,60], help="Intraday stock minutes")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return [s_ticker, s_start, s_interval, df_stock]

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Update values:
    s_ticker = ns_parser.s_ticker
    s_start = ns_parser.s_start_date
    s_interval = str(ns_parser.n_interval)+'min'

    try:
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        # Daily
        if s_interval == "1440min":
            df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=ns_parser.s_ticker, outputsize='full')     
        # Intraday
        else: 
            df_stock, d_stock_metadata = ts.get_intraday(symbol=ns_parser.s_ticker, outputsize='full', interval=s_interval)  
            
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return [s_ticker, s_start, s_interval, df_stock]

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        # Slice dataframe from the starting date YYYY-MM-DD selected
        df_stock = df_stock[ns_parser.s_start_date:]
        print(f"Loading {s_intraday} {s_ticker} stock with starting period {s_start.strftime('%Y-%m-%d')} for analysis.")
    else:
        print(f"Loading {s_intraday} {s_ticker} stock for analysis.")

    return [s_ticker, s_start, s_interval, df_stock]


# ----------------------------------------------------- VIEW -----------------------------------------------------
def view(l_args, s_ticker, s_start, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='view', description='Visualise historical data of a stock. An alpha_vantage key is necessary.')
    if s_ticker:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", default=s_ticker, help='Stock ticker')  
    else:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help='Stock ticker')
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date", help="The starting date (format YYYY-MM-DD) of the stock")
    parser.add_argument('-i', "--interval", action="store", dest="n_interval", type=int, default=0, choices=[1,5,15,30,60], help="Intraday stock minutes")
    parser.add_argument("--type", action="store", dest="n_type", type=check_positive, default=5, # in case it's daily
                        help='1234 corresponds to types: 1. open; 2. high; 3.low; 4. close; while 14 corresponds to types: 1.open; 4. close')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Update values:
    s_ticker = ns_parser.s_ticker
    if ns_parser.s_start_date:
        s_start = ns_parser.s_start_date

    # A new interval intraday period was given
    if ns_parser.n_interval != 0:
        s_interval = str(ns_parser.n_interval)+'min'

    try:
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        # Daily
        if s_interval == "1440min":
            df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')
        # Intraday
        else:
            df_stock, d_stock_metadata = ts.get_intraday(symbol=s_ticker, outputsize='full', interval=s_interval)  
              
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return

    # Slice dataframe from the starting date YYYY-MM-DD selected
    df_stock = df_stock[s_start:]

    # Daily
    if s_interval == "1440min":
         # The default doesn't exist for intradaily data
        ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
        if 4 not in ln_col_idx:
            ln_col_idx.append(4)
        # Check that the types given are not bigger than 4, as there are only 5 types (0-4)
        if len([i for i in ln_col_idx if i > 4]) > 0:
            print("An index bigger than 4 was given, which is wrong. Try again")
            return
        # Append last column of df to be filtered which corresponds to: 6. Volume
        ln_col_idx.append(5) 
    # Intraday
    else:
        # The default doesn't exist for intradaily data
        if ns_parser.n_type == 5:
            ln_col_idx = [3]
        else:
            ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
        # Check that the types given are not bigger than 3, as there are only 4 types (0-3)
        if len([i for i in ln_col_idx if i > 3]) > 0:
            print("An index bigger than 3 was given, which is wrong. Try again")
            return
        # Append last column of df to be filtered which corresponds to: 5. Volume
        ln_col_idx.append(4) 

    # Plot view of the stock
    plot_view_stock(df_stock.iloc[:, ln_col_idx], ns_parser.s_ticker)


# ----------------------------------------------------- HELP ------------------------------------------------------------------
def print_help(s_ticker, s_start, s_interval, b_is_market_open):
    """ Print help
    """
    print("What do you want to do?")
    print("   help        help to see this menu again")
    print("   quit        to abandon the program")
    print("")
    print("   clear       clear a specific stock ticker from analysis")
    print("   load        load a specific stock ticker for analysis")
    print("   view        view and load a specific stock ticker for technical analysis")
    print("   disc        discovery menu to find trending stocks")

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]
    if s_ticker and s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    elif s_ticker:
        print(f"\n{s_intraday} Stock: {s_ticker}")
    else:
        print("\nStock: ?")
    print(f"Market {('CLOSED', 'OPEN')[b_is_market_open]}.")

    if s_ticker:
        print("\nMenus:")
        #print("   sen         sentiment of the market, \t from: reddit, stocktwits, twitter")
        print("   fa          fundamental analysis,    \t e.g.: income, balance, cash, earnings")
        print("   ta          technical analysis,      \t e.g.: ema, macd, rsi, adx, bbands, obv")
        print("")
        print("   dd          in-depth due-diligence,  \t e.g.: news, analyst, shorts, insider, sec")
        #print("")
        #print("   pred        prediction techniques,   \t e.g.: regression, arima, rnn, lstm, prophet")

    '''
        print("\nPrediction:")
        print("   ma")
        print("   ema")
        print("   lr")
        print("   knn")
        print("   arima")
        print("   rnn")
        print("   lstm")
        print("   prophet")
    '''


# -----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function of the program
    """ 

    s_ticker = ""
    s_start = ""
    df_stock = pd.DataFrame()
    b_intraday = False
    s_interval = "1440min"

    # Set stock by default to speed up testing
    s_ticker = "AMZN"
    s_start = datetime.strptime("2020-06-04", "%Y-%m-%d")
    ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')  
    df_stock = df_stock[s_start:] 
    # Delete above in the future

    # Add list of arguments that the main parser accepts
    menu_parser = argparse.ArgumentParser(prog='stock_market_bot', add_help=False)
    menu_parser.add_argument('opt', choices=['help', 'quit', 'q',
                                             'clear', 'load', 'view',
                                             'disc', 'fa', 'ta', 'dd'])
                                             

    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
    print("\n")

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')

        # Is command empty
        if not len(as_input):
            print("")
            continue
        
        # Parse main command of the list of possible commands
        try:
            (ns_known_args, l_args) = menu_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.opt == 'help':
            print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        elif (ns_known_args.opt == 'quit') or (ns_known_args.opt == 'q'):
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            return
       
        elif ns_known_args.opt == 'clear':
            print("Clearing stock ticker to be used for analysis")
            s_ticker = ""
            s_start = ""

        elif ns_known_args.opt == 'load':
            [s_ticker, s_start, s_interval, df_stock] = load(l_args, s_ticker, s_start, s_interval, df_stock)

        elif ns_known_args.opt == 'view':
            view(l_args, s_ticker, s_start, s_interval, df_stock)

        # DISCOVERY MENU
        elif ns_known_args.opt == 'disc':
            b_quit = dm.disc_menu()

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # FUNDAMENTAL ANALYSIS MENU
        elif ns_known_args.opt == 'fa':
            b_quit = fam.fa_menu(s_ticker, s_start, s_interval)

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # TECHNICAL ANALYSIS MENU
        elif ns_known_args.opt == 'ta':
            b_quit = tam.ta_menu(df_stock, s_ticker, s_start, s_interval)

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # DUE DILIGENCE MENU
        elif ns_known_args.opt == 'dd':
            b_quit = ddm.dd_menu(s_ticker, s_start, s_interval)

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        else:
            print('Shouldnt see this command!')

        print("")

if __name__ == "__main__":
    main()
