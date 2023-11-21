#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  CoinHelperCheck.py
#  
#  Copyright 2021 k-aito <77667659+k-aito@users.noreply.github.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


def main(args):
  import csv
  import json
  import os
  import requests

  # Write your CoinMarketCap API
  from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
  cmc = CoinMarketCapAPI('XXX')

  from notifypy import Notify
  notification = Notify()
  notification.title = "CoinHelperCheck"

  # Move db.csv to db.csv.old
  try:
    os.replace('db.csv', 'db.csv.old')
  # Maybe it's already moved
  except FileNotFoundError:
    pass

  with open('db.csv.old', newline='') as csvfile_read:
    reader = csv.reader(csvfile_read, delimiter='|')
    with open('db.csv', 'w', newline='') as csvfile_write:
      writer = csv.writer(csvfile_write, delimiter='|')
      for row in reader:
        try:
          action      = row[0]
          symbol      = row[1].upper()

          ## BUY
          if action == 'buy':
            # Define the other's field of the CSV
            lowestPrice  = float(row[2])
          
            # Does the coinValue is under lowestPrice
            coinValue = cmc.cryptocurrency_quotes_latest(symbol=symbol, convert='EUR').data[symbol]['quote']['EUR']['price']
            
            # We got benefit or not
            if coinValue < lowestPrice:
              print("---")
              print("ACTION: {}".format(action))
              print("The value of {} dropped under your lowest price".format(symbol))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual lowest price: {}€".format(lowestPrice))
              writer.writerow(['buy', symbol, lowestPrice])
              notification.message = "The value of {} dropped under your lowest price".format(symbol)
              notification.send(block=False)
            else:
              print("---")
              print("ACTION: {}".format(action))
              print("The value of {} didn't drop under your lowest price".format(symbol))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual lowest price: {}€".format(lowestPrice))
              writer.writerow(['buy', symbol, lowestPrice])

          ## SELL
          elif action == 'sell':
            # Define the other's field of the CSV
            amountEuro  = float(row[2])
            amountCoin  = float(row[3])
            winPercent  = float(row[4])
            waitPercent = float(row[5])
          
            # Do we got benefit
            coinValue = cmc.cryptocurrency_quotes_latest(symbol=symbol, convert='EUR').data[symbol]['quote']['EUR']['price']
            ourValue = amountCoin * coinValue
            wantedBenefit = (amountEuro*winPercent)/100
            totalWithBenefit = amountEuro+wantedBenefit
            
            # We got benefit or not
            if amountEuro + wantedBenefit < ourValue:
              print("---")
              print("ACTION: {}".format(action))
              print("You got your benefit for {}".format(symbol))
              print("Invest: {}€".format(amountEuro))
              print("Wanted benefit: {}% -> {}€".format(winPercent, wantedBenefit))
              print("Total with benefit wanted: {}€".format(totalWithBenefit))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual value: {}€".format(ourValue))

              # Set to wait
              writer.writerow(['wait', symbol, amountEuro, amountCoin, ourValue, waitPercent])
              notification.message = "You got benefit for {} and it's not set to wait action".format(symbol)
              notification.send(block=False)
            else:
              print("---")
              print("ACTION: {}".format(action))
              print("You didn't get your benefit yet for {}".format(symbol))
              print("Invest: {}€".format(amountEuro))
              print("Wanted benefit: {}% -> {}€".format(winPercent, wantedBenefit))
              print("Total with benefit wanted: {}€".format(totalWithBenefit))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual value: {}€".format(ourValue))
              writer.writerow(['sell', symbol, amountEuro, amountCoin, winPercent, waitPercent])

          ## WAIT
          elif action == 'wait':
            # Define the other's field of the CSV
            amountEuro  = float(row[2])
            amountCoin  = float(row[3])
            oldValue  = float(row[4])
            waitPercent = float(row[5])

            # Do we have dropped under the maximum of dropPercent
            coinValue = cmc.cryptocurrency_quotes_latest(symbol=symbol, convert='EUR').data[symbol]['quote']['EUR']['price']
            ourValue = amountCoin * coinValue
            dropValue = (ourValue*waitPercent)/100
            minimumWithDrop = oldValue - dropValue

            # Value to be saved in db
            if oldValue < ourValue:
              saveValue = ourValue
            else:
              saveValue = oldValue
            
            # We check if the ourValue is bigger than our oldValue - dropValue (authorized drop)
            if ourValue < minimumWithDrop:
              print("---")
              print("ACTION: {}".format(action))
              print("Value dropped for {}".format(symbol))
              print("Invest: {}€".format(amountEuro))
              print("Maximum drop: {}% -> {}€".format(waitPercent, dropValue))
              print("The value may not go lower than: {}€".format(minimumWithDrop))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual value: {}€".format(ourValue))
              print("Your previous value: {}€".format(oldValue))
              writer.writerow(['wait', symbol, amountEuro, amountCoin, saveValue, waitPercent])
              notification.message = "Your value dropped for {}".format(symbol)
              notification.send(block=False)
            else:
              print("---")
              print("ACTION: {}".format(action))
              print("The value didn't drop or still in the authorized drop for {}".format(symbol))
              print("Invest: {}€".format(amountEuro))
              print("Maximum drop: {}% -> {}€".format(waitPercent, dropValue))
              print("The value may not go lower than: {}€".format(minimumWithDrop))
              print("Actual coin value: {}€".format(coinValue))
              print("Your actual value: {}€".format(ourValue))
              print("Your previous value: {}€".format(oldValue))
              writer.writerow(['wait', symbol, amountEuro, amountCoin, saveValue, waitPercent])

          ## REDEEM
          if action == 'redeem':
            # Define the other's field of the CSV
            amountCoin  = float(row[2])
            maxAmountEuro  = float(row[3])
          
            # Does ourValue is above maxAmountEuro
            coinValue = cmc.cryptocurrency_quotes_latest(symbol=symbol, convert='EUR').data[symbol]['quote']['EUR']['price']
            ourValue = amountCoin * coinValue
            
            # We got benefit or not
            if ourValue > maxAmountEuro:
              print("---")
              print("ACTION: {}".format(action))
              print("It's time to redeem your {}".format(symbol))
              print("Your number of coins is {} => {}€".format(amountCoin, ourValue))
              print("Your actual redeem level: {}€".format(maxAmountEuro))
              writer.writerow(['redeem', symbol, amountCoin, maxAmountEuro])
              notification.message = "It's time to redeem your {}".format(symbol)
              notification.send(block=False)
            else:
              print("---")
              print("ACTION: {}".format(action))
              print("It's not the time to redeem your {}".format(symbol))
              print("Your number of coins is {} => {}€".format(amountCoin, ourValue))
              print("Your actual redeem level: {}€".format(maxAmountEuro))
              writer.writerow(['redeem', symbol, amountCoin, maxAmountEuro])

        # In case row is empty
        except IndexError:
          # Keep the row that we add in db.csv for our formatting
          writer.writerow(row)
          continue

  return 0

if __name__ == '__main__':
  import sys
  sys.exit(main(sys.argv))
