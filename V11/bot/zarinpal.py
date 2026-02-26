import aiohttp
import logging

logger = logging.getLogger("ZarinPal")

class ZarinPal:
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id
        self.request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
        self.gateway_url = "https://www.zarinpal.com/pg/StartPay/"

    async def request_payment(self, amount, description, callback_url, mobile=None, email=None):
        """
        درخواست پرداخت از زرین‌پال
        amount: مبلغ به تومان
        """
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "description": description,
            "callback_url": callback_url,
            "metadata": {
                "mobile": mobile,
                "email": email
            }
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.request_url, json=data, timeout=10.0) as response:
                    res_data = await response.json()
                    if res_data.get('data') and res_data['data'].get('authority'):
                        authority = res_data['data']['authority']
                        return f"{self.gateway_url}{authority}", authority
                    else:
                        logger.error(f"ZarinPal Request Error: {res_data}")
                        return None, None
        except Exception as e:
            logger.error(f"ZarinPal Exception: {e}")
            return None, None

    async def verify_payment(self, amount, authority):
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "authority": authority
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.verify_url, json=data, timeout=10.0) as response:
                    res_data = await response.json()
                    if res_data.get('data') and res_data['data'].get('code') == 100:
                        return True, res_data['data'].get('ref_id')
                    else:
                        return False, res_data.get('errors')
        except Exception as e:
            logger.error(f"ZarinPal Verify Exception: {e}")
            return False, str(e)
