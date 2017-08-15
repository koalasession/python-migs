from collections import OrderedDict
from hashlib import sha256
import hmac
'''
*  Migs 3rd party payment
'''


class Migs(object):

    def __init__(self, merchant_id, access_code, secret, currency, locale,
                 service_url='https://migs.mastercard.com.au/vpcpay'):
        self.merchant_id = merchant_id
        self.access_code = access_code
        self.secret = secret
        self.currency = currency
        self.locale = locale
        self.service_url = service_url

    def generate_order(self, order):
        '''
            returns an order object
            order is a dict must contain
            vpc_MerchTxnRef
            vpc_OrderInfo
            vpc_Amount
            vpc_ReturnURL
        '''
        order['vpc_Version'] = 1
        order['vpc_Command'] = 'pay'
        order['vpc_Merchant'] = self.merchant_id
        order['vpc_AccessCode'] = self.access_code
        order['vpc_Currency'] = self.currency
        order['vpc_Locale'] = self.locale

        order = OrderedDict(sorted(order.items()))
        self.order = order
        return self.order

    def generate_payment_link(self):
        '''
            returns a payment link
        '''
        self.order['vpc_SecureHash'] = self.generate_hash(self.order)

        self.order['vpc_SecureHashType'] = 'SHA256'
        return self.service_url + '?' + '&'.join(
            '{}={}'.format(key, val) for key, val in self.order.items())

    def generate_hash(self, order):
        '''
            converts the ordered dict (by key) items as key=value
            then joined by &, then hashed using  SHA-256 HMAC algorithm
            using the hex decoded value of your merchant secret as the key
        '''

        hash_string = '&'.join('{}={}'.format(key, val)
                               for key, val in order.items())
        securehash = hmac.new(bytes.fromhex(self.secret),
                              hash_string.encode(),
                              sha256).hexdigest().upper()

        return securehash

    def verify_response(self, res_dict):
        '''
            compares response fields with own fields
            then if successful passes to verifying the hash
            sets state and message
        '''
        status_array = ('vpc_Command',
                        'vpc_Merchant',
                        'vpc_Currency',
                        'vpc_MerchTxnRef',
                        'vpc_OrderInfo',
                        'vpc_Amount')
        if self.verify_response_hash(res_dict):
            for st in status_array:
                if st in self.order and st in res_dict:
                    if self.order[st] != res_dict[st]:
                        print(st)
                        print(type(self.order[st]))
                        print(type(res_dict[st]))
                        self.message = self.response_desc('X-X')
                        self.state = False

    def verify_response_hash(self, res_dict):
        '''
            Compares generated hash with received hash
            sets state and message
        '''
        self.message = self.response_desc(res_dict['vpc_TxnResponseCode'])

        if res_dict['vpc_TxnResponseCode'] != '0':
            self.state = False
        else:
            res_dict.pop('vpc_SecureHashType', None)
            res_secure_hash = res_dict.pop('vpc_SecureHash', None)
            secure_hash = self.generate_hash(
                OrderedDict(sorted(res_dict.items())))
            self.state = res_secure_hash == secure_hash
            if self.state is False:
                self.message = self.response_desc('X-X')
        return self.state

    def response_desc(self, x):
        '''
            returns a response based on code
        '''
        return {
            '0': 'Transaction Successful',
            '?': 'Transaction status is unknown',
            '1': 'Unknown Error',
            '2': 'Bank Declined Transaction',
            '3': 'No Reply from Bank',
            '4': 'Expired Card',
            '5': 'Insufficient funds',
            '6': 'Error Communicating with Bank',
            '7': 'Payment Server System Error',
            '8': 'Transaction Type Not Supported',
            '9': 'Bank declined transaction (Do not contact Bank)',
            'A': 'Transaction Aborted',
            'B': 'Transaction Blocked',
            'C': 'Transaction Cancelled',
            'D': 'Deferred transaction has been received and is \
                    awaiting processing',
            'F': '3D Secure Authentication failed',
            'I': 'Card Security Code verification failed',
            'L': 'Shopping Transaction Locked (Please try the transaction \
                    again later)',
            'N': 'Cardholder is not enrolled in Authentication scheme',
            'P': 'Transaction has been received by the Payment Adaptor and is \
                    being processed',
            'R': 'Transaction was not processed - Reached limit of retry \
                    attempts allowed',
            'S': 'Duplicate SessionID (OrderInfo)',
            'T': 'Address Verification Failed',
            'U': 'Card Security Code Failed',
            'V': 'Address Verification and Card Security Code Failed',
            'X-X': 'Payment Has ERRORS',
        }.get(x, 'Unable to be determined')
