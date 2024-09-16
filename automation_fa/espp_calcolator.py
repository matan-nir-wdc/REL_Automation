if __name__ == "__main__":
    salary = input("enter salary(monthly): ")
    percent = input("percent of ESPP: ")
    dollar = input("ILS to USD: ")
    stock_start = input("WDC stock in USD(at the start): ")
    stock_end = input("WDC stock in USD(at the end): ")
    stock_lower = float(stock_start) if float(stock_start) < float(stock_end) else float(stock_end)
    stock_high = float(stock_end)
    amount_vasted = float(salary) * 6 * float(float(percent) / 100)
    print("Pay taxes in salary: " + str(float(amount_vasted)))
    amount_vasted = amount_vasted / float(dollar)
    stock_after_discount = stock_lower * 0.95
    amount_of_stocks = amount_vasted / stock_after_discount
    value_in_money = int(amount_of_stocks) * float(stock_high)
    value_in_money = value_in_money * float(dollar)
    already_pay_taxes = amount_vasted * float(dollar)
    taxes = value_in_money - already_pay_taxes
    print("earn money: " + str(taxes))
    print("need to pay taxes: " + str(taxes))
    taxes = float(taxes) * 0.65
    taxes = taxes - (25 * float(dollar))
    print("worst case money earn after taxes (35%+ 25$ commission): " + str(taxes))
    print("enter you bank account: " + str(float(already_pay_taxes) + float(taxes)))
    stock_end = input("Press any key to exit")

