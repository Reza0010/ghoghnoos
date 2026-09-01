import aiohttp
import json
import logging

logger = logging.getLogger("ZarinPal")

class ZarinPal:
    def __init__(self, merchant_id):
        self.merchant_id = merchant_id
        self.request_url = "https://api.zarinpal.com/pg/v4/payment/request.json"
        self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json"
        self.payment_page = "https://www.zarinpal.com/pg/StartPay/"

    async def create_payment(self, amount, description, callback_url, mobile=None, email=None):
        """
        ایجاد تراکنش جدید
        amount: به تومان
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount), # زرین پال v4 به تومان است
            "description": description,
            "callback_url": callback_url,
            "metadata": {}
        }
        if mobile: payload["metadata"]["mobile"] = mobile
        if email: payload["metadata"]["email"] = email

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.request_url, json=payload, timeout=10) as resp:
                    result = await resp.json()
                    if result.get("data") and result["data"].get("authority"):
                        authority = result["data"]["authority"]
                        return {
                            "status": True,
                            "authority": authority,
                            "url": f"{self.payment_page}{authority}"
                        }
                    else:
                        logger.error(f"ZarinPal Request Error: {result}")
                        return {"status": False, "error": result.get("errors")}
        except Exception as e:
            logger.error(f"ZarinPal Connection Error: {e}")
            return {"status": False, "error": str(e)}

    async def verify_payment(self, amount, authority):
        """
        تایید تراکنش
        """
        payload = {
            "merchant_id": self.merchant_id,
            "amount": int(amount), # تومان
            "authority": authority
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.verify_url, json=payload, timeout=10) as resp:
                    result = await resp.json()
                    if result.get("data") and result["data"].get("code") in [100, 101]:
                        return {
                            "status": True,
                            "ref_id": result["data"]["ref_id"],
                            "code": result["data"]["code"]
                        }
                    else:
                        logger.error(f"ZarinPal Verify Error: {result}")
                        return {"status": False, "error": result.get("errors")}
        except Exception as e:
            logger.error(f"ZarinPal Verify Connection Error: {e}")
            return {"status": False, "error": str(e)}
