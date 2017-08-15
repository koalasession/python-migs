# python-migs
## 3rd party payment using migs
## Migs payment in python3

### example usage:

```python
from migs import Migs

## generate order

migs = Migs(merchant_id,
            access_code,
            secret,
            currency,
            locale)
order = {
    'vpc_MerchTxnRef': 'generated receipt no.',
    'vpc_OrderInfo': 'general_string perhaps the id of a stored object',
    'vpc_Amount': 'amount multiplied by 100 no decimals',
    'vpc_ReturnURL': 'callback url',
}
migs.generate_order(order)
payment_url = migs.generate_payment_link()

## redirect to payment_url

## after callback
migs = Migs(merchant_id,
            access_code,
            secret,
            currency,
            locale)
order = {
    'vpc_MerchTxnRef': response['vpc_MerchTxnRef'] ,
    'vpc_OrderInfo': response['vpc_OrderInfo'] ,
    'vpc_Amount': response['vpc_Amount'] ,
    'vpc_ReturnURL': 'same callback url' ,
}

try:
    migs.generate_order(order)
    migs.verify_response(res_dict)
    if migs.state:
        ## payment successful
        ...
    else:
        ## payment failed
        print(migs.message)
        ...
except Exception as e:
    print(e)
```
