import asyncio
import dns.resolver
from typing import Dict

class DNSService:
    @staticmethod
    async def verify_domain(domain: str) -> Dict[str, any]:
        # Using the system event loop to prevent blocking async runtime operations
        loop = asyncio.get_event_loop()
        results = {
            "mx_valid": False,
            "spf_valid": False,
            "dmarc_valid": False,
            "mx_records": []
        }
        
        # 1. Look up Mail Exchange (MX) records to see if the domain can accept emails
        try:
            mx_answers = await loop.run_in_executor(None, lambda: dns.resolver.resolve(domain, 'MX'))
            results["mx_records"] = [str(r.exchange).strip('.') for r in mx_answers]
            results["mx_valid"] = len(results["mx_records"]) > 0
        except Exception:
            results["mx_valid"] = False

        # 2. Look up SPF text records to check authorization markers
        try:
            txt_answers = await loop.run_in_executor(None, lambda: dns.resolver.resolve(domain, 'TXT'))
            for r in txt_answers:
                txt_str = "".join([part.decode('utf-8') for part in r.strings])
                if txt_str.startswith("v=spf1"):
                    results["spf_valid"] = True
                    break
        except Exception:
            results["spf_valid"] = False

        # 3. Look up DMARC alignment validation rules
        try:
            dmarc_answers = await loop.run_in_executor(None, lambda: dns.resolver.resolve(f"_dmarc.{domain}", 'TXT'))
            for r in dmarc_answers:
                txt_str = "".join([part.decode('utf-8') for part in r.strings])
                if txt_str.startswith("v=DMARC1"):
                    results["dmarc_valid"] = True
                    break
        except Exception:
            results["dmarc_valid"] = False

        return results