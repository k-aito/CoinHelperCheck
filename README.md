# CoinHelperCheck

⚠️ Surely broken and currently not supported ⚠️

💙 You are welcome to make a PR to fix 💙

## Setup

```
python3 -m venv ./env
. ./env/bin/activate
pip install requests
pip install notify-py
pip install python-coinmarketcap
```

## Test if notifications work

```
. ./env/bin/activate
python3

# In python copy paste
from notifypy import Notify

notification = Notify()
notification.title = "Cool Title"
notification.message = "Even cooler message."

notification.send()
```

## Schedule run with command line

```
# Use your venv
. ./env/bin/activate

min=10
seconds=$((60*min))
while true ; do
  clear
  msg=$(date)
  msg="$msg$(python3 ./CoinHelperCheck.py)"
  printf '%s\n\n' "$msg"
  printf '%s\n\n' "$msg" >> /tmp/coinhelpercheck.log
  sleep "$seconds"
done
```

## Goal

Have a way to notify users about their investment based on simple rules

- Invest only what you can lose
- Define an amount to spend for a defined time
- Choose investments based on your interest in the goal because, remember, monkeys guess better than us randomly
  - https://medium.com/diamond-hand-investing/even-monkeys-can-beat-the-market-really-f411fcc52cce
  - https://www.businessinsider.com.au/monkeys-are-better-stock-pickers-than-fund-managers-experiment-2013-4
- Define a win percent on the long term
- When the win percentage is passed, be notified again when the price drops

## DB

Types of actions:

- buy     : notify you when to buy when the price is the lowest
- sell    : notify you when your benefit percent it reached
- wait    : notify you when your benefit percent drop below
- redeem  : notify you when your money got above a certain amount so that you remember to redeem

### Buy

```
buy|coin symbol (btc)|lowest coin price
```

### Sell

```
sell|coin symbol (btc)|amount euro|amount coin|win percent for notify|beneficit percent for wait
```

### Wait

```
wait|coin symbol (btc)|amount euro|amount coin|our actual value in euro or old value if we didn't pass the waitPercent|benefit percent to be notified when it drop
```

### Redeem

```
redeem|coin symbol (btc)|amount coint|limit amount eur to be notified
```
