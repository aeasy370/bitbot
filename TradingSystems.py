import cbpro
import time
import var
import phrase

BUY = 'buy'
SELL = 'sell'

def auth():
    auth = cbpro.AuthenticatedClient(phrase.api_public, phrase.api_secret, phrase.passphrase, api_url='https://api-public.sandbox.pro.coinbase.com')
    return TradingSystems(auth)

class TradingSystems:
    # member functions:
    def __init__(self, cb_pro_client):
        self.client = cb_pro_client
        self.currentPrice = float(self.getPriceBTC())
        self.buyIn = self.currentPrice * var.BUYper
        self.cashOut = self.currentPrice * var.SELLper
        self.boughAt = 0.0
        self.productStats = self.client.get_product_24hr_stats('BTC-USD')
        print(self.balance('USD'))
        print(self.balance('BTC'))
        print(self.productStats)


    def trade(self, action, limitPrice, quantity):
        if action == BUY:
            print('size=',self.round(quantity))
            rep = self.client.buy(
                price=limitPrice,
                size=self.round(quantity * 0.98),
                order_type='limit',
                product_id='BTC-USD',
                overdraft_enabled=False
                )
        elif action == SELL:
            rep = self.client.sell(
                price=limitPrice,
                size=quantity,
                order_type='limit',
                product_id='BTC-USD',
                overdraft_enabled=False
                )

        print(rep)

    def viewAccounts(self, accountCurrency):
        accounts = self.client.get_accounts()

        account = list(filter(lambda x: x['currency'] == accountCurrency, accounts))[0]
        return account

    def viewOrder(self, order_id):
        pass

    def balance(self, currency):
        return float(self.viewAccounts(currency)['balance'])

    def getPriceBTC(self):
        tick = self.client.get_product_ticker(product_id='BTC-USD')
        return float(tick['bid'])

    def round(self, val):
        newval = int(val * 10000000)/10000000
        return newval

    def buy(self):
        print('Buying')
        currentPrice = self.getPriceBTC()
        USDbalance = self.viewAccounts('USD')['balance']
        self.boughAt = currentPrice
        self.cashOut = currentPrice * 0.99
        self.trade(BUY, float(currentPrice), (float(USDbalance) * 0.5) / float(currentPrice))

    def sell(self):
        print('Selling')
        currentPrice = self.getPriceBTC()
        self.trade(SELL, currentPrice, self.viewAccounts('BTC')['balance'])

    def buyTest(self):
        if (self.balance('USD') * 0.5) >= (self.currentPrice * 0.001) * 1.001:
            if self.currentPrice > self.buyIn:
                return True
        return False

    def sellTest(self):
        if self.balance('BTC'):
            if self.currentPrice < self.cashOut:
                return True
        return False

    def printVal(self):
        print('\nValue', float(self.viewAccounts('BTC')['balance']) * self.getPriceBTC() + float(self.viewAccounts('USD')['balance']))
        print(self.balance('USD'))
        print(self.balance('BTC'))
        print('buyIn =', self.buyIn)
        print('Current Price =', self.currentPrice)
        print('cashOut =', self.cashOut)

    def update(self):
        time.sleep(30)
        self.currentPrice = self.getPriceBTC()
        if self.balance('BTC') and self.currentPrice > self.boughAt:
            if (self.currentPrice * 0.99) > self.cashOut:
                self.cashOut = self.currentPrice * var.SELLper
        elif self.balance('USD') and self.currentPrice < self.boughAt:
            self.buyIn = self.currentPrice * var.BUYper
        if self.balance('BTC') == 0 and self.currentPrice < self.cashOut:
            self.cashOut = self.currentPrice * var.SELLper
            self.buyIn = self.currentPrice * var.BUYper
