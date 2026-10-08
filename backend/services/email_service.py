from typing import Dict, List
from email_validator import validate_email, EmailNotValidError
from services.dns_service import DNSService
# Known disposable email providers list
DISPOSABLE_DOMAINS = {"yopmail.com", "mailinator.com", "10minutemail.com", "tempmail.com", "guerrillamail.com"}

class EmailService:
    @staticmethod
    async def verify_address(email: str) -> Dict[str, any]:
        reasons: List[str] = []
        passed: List[str] = []
        failed: List[str] = []
        
        # 1. Syntax Validation
        try:
            valid = validate_email(email, check_deliverability=False)
            domain = valid.domain
            passed.append("Email syntax structure is valid.")
        except EmailNotValidError as e:
            return {
                "decision": "BLOCK",
                "trust_score": 0,
                "confidence": 100,
                "risk": "High",
                "reasons": [f"Invalid syntax layout: {str(e)}"],
                "recommendation": "Reject execution. The syntax does not conform to RFC specifications.",
                "checks_passed": [],
                "checks_failed": ["Syntax validation"]
            }

        # 2. Disposable Email Check
        is_disposable = domain.lower() in DISPOSABLE_DOMAINS
        if is_disposable:
            failed.append("Disposable provider detected")
            reasons.append(f"Domain '{domain}' belongs to a known temporary/disposable email utility.")
        else:
            passed.append("Domain is not classified under standard disposable providers.")

        # 3. DNS Lookup Metrics
        dns_metrics = await DNSService.verify_domain(domain)
        
        if dns_metrics["mx_valid"]:
            passed.append("Valid MX Records configured for target infrastructure.")
        else:
            failed.append("Missing MX Records")
            reasons.append("Domain has no valid Mail Exchange (MX) records; cannot safely process inbound relays.")

        if dns_metrics["spf_valid"]:
            passed.append("SPF authentication record discovered.")
        else:
            failed.append("Missing SPF record")
            reasons.append("Domain lacks an SPF authorization payload, magnifying spoofing vulnerabilities.")

        if dns_metrics["dmarc_valid"]:
            passed.append("DMARC enforcement configuration found.")
        else:
            failed.append("Missing DMARC record")
            reasons.append("DMARC tracking alignment is missing on the parent domain framework.")

        # Unified scoring algorithm rules
        base_score = 100
        if not dns_metrics["mx_valid"]: base_score -= 40
        if not dns_metrics["spf_valid"]: base_score -= 20
        if not dns_metrics["dmarc_valid"]: base_score -= 15
        if is_disposable: base_score -= 25
        
        trust_score = max(0, base_score)
        confidence = 95 if dns_metrics["mx_valid"] else 70

        if trust_score >= 80:
            decision, risk, rec = "ALLOW", "Low", "Proceed with low risk routing infrastructure parameters."
        elif trust_score >= 45:
            decision, risk, rec = "WARN", "Medium", "Exercise caution. Verify secondary domain out-of-band signals before internal relay."
        else:
            decision, risk, rec = "BLOCK", "High", "Drop vector immediately. Technical trust markers indicate high risk anomalies."

        return {
            "decision": decision,
            "trust_score": trust_score,
            "confidence": confidence,
            "risk": risk,
            "reasons": reasons if reasons else ["All domain technical configurations conform to security policies."],
            "recommendation": rec,
            "checks_passed": passed,
            "checks_failed": failed
        }