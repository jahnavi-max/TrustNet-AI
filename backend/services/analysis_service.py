import re
from typing import Dict, List

class ContentAnalysisService:
    # Heuristic signature rules weights
    PHISHING_MARKERS = {
        r"(?i)(verify your account|update your wallet|confirm banking password|security alert resolve)": 25,
        r"(?i)(urgent response required|immediate action|unauthorized transaction notice|within 24 hours)": 20,
        r"(?i)(wire transfer authorization|ceo request|overdue payment invoice|gift card purchase)": 25,
        r"(?i)(login to portal|credential mismatch protection|click link below to update)": 20
    }

    @staticmethod
    async def analyze_content(sender: str, subject: str, body: str) -> Dict[str, any]:
        combined_payload = f"{subject} {body}"
        reasons: List[str] = []
        score_deduction = 0

        # Run heuristic scanning matching threat signatures
        for pattern, weight in ContentAnalysisService.PHISHING_MARKERS.items():
            if re.search(pattern, combined_payload):
                score_deduction += weight
                reasons.append(f"Heuristic flag matched threat signature structural pattern (Impact Vector: -{weight} pts)")

        # URL Extractor Engine Regex
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, combined_payload)
        extracted_domains = []
        
        for url in urls:
            domain_match = re.search(r'https?://([^/\s]+)', url)
            if domain_match:
                extracted_domains.append(domain_match.group(1))

        if urls:
            reasons.append(f"Discovered {len(urls)} inline hyper-links mapped for threat intelligence adapters processing.")
            
        # Basic Domain Mismatch Validation
        sender_domain_match = re.search(r'@([^/\s]+)', sender)
        if sender_domain_match and extracted_domains:
            s_dom = sender_domain_match.group(1).lower()
            mismatch_found = any(s_dom not in d.lower() for d in extracted_domains)
            if mismatch_found:
                score_deduction += 15
                reasons.append("Structural mismatch observed between sender profile routing domain and inside link nodes.")

        trust_score = max(0, 100 - score_deduction)
        confidence = 90

        if trust_score >= 80:
            decision, risk, rec = "ALLOW", "Low", "Content metrics pass normal behavioral standard frameworks."
        elif trust_score >= 50:
            decision, risk, rec = "WARN", "Medium", "Elevated social engineering indicators observed. Scan payloads with sandbox systems."
        else:
            decision, risk, rec = "BLOCK", "High", "Critical risk detected. Payload matches credential harvesting, fraud, or BEC behaviors."

        return {
            "decision": decision,
            "trust_score": trust_score,
            "confidence": confidence,
            "risk": risk,
            "reasons": reasons if reasons else ["No hostile patterns, threat indicators, or social engineering matrices detected."],
            "recommendation": rec,
            "extracted_urls": urls,
            "extracted_domains": list(set(extracted_domains))
        }