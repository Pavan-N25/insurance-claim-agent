from typing import Dict, Any, List

class NotificationService:
    @staticmethod
    def generate_customer_communication(
        status: str,
        claim_id: str,
        claimant_name: str,
        missing_docs: List[str] = [],
        language: str = "en"
    ) -> Dict[str, str]:
        """
        Generates professional customer status messages in English, Hindi, and Kannada.
        """
        templates = {
            "en": {
                "SUBMITTED": {
                    "subject": f"Claim #{claim_id} Received - Under Initial Triage",
                    "body": f"Dear {claimant_name}, we have received your insurance claim (#{claim_id}). Our automated multimodal triage pipeline is currently reviewing your submitted evidence."
                },
                "REQUEST_INFO": {
                    "subject": f"Action Required: Additional Documentation for Claim #{claim_id}",
                    "body": f"Dear {claimant_name}, to expedite processing of claim #{claim_id}, please upload the following missing document(s): {', '.join(missing_docs) if missing_docs else 'Clear photos of incident area'}."
                },
                "APPROVED": {
                    "subject": f"Claim #{claim_id} Approved",
                    "body": f"Dear {claimant_name}, great news! Your claim (#{claim_id}) has been approved. The settlement processing has been initiated to your designated account."
                },
                "REJECTED": {
                    "subject": f"Important Update Regarding Claim #{claim_id}",
                    "body": f"Dear {claimant_name}, following thorough assessment of policy terms and incident evidence, claim #{claim_id} could not be approved. Please review your portal for details."
                },
                "MANUAL_REVIEW": {
                    "subject": f"Claim #{claim_id} Assigned for Specialist Review",
                    "body": f"Dear {claimant_name}, your claim (#{claim_id}) has been assigned to a senior claims adjuster for detailed verification. We will update you shortly."
                }
            },
            "hi": {
                "SUBMITTED": {
                    "subject": f"दावा #{claim_id} प्राप्त हुआ - प्रारंभिक जांच जारी",
                    "body": f"प्रिय {claimant_name}, हमें आपका बीमा दावा (#{claim_id}) प्राप्त हुआ है। हमारा सिस्टम वर्तमान में आपके दस्तावेजों और साक्ष्यों की जांच कर रहा है।"
                },
                "REQUEST_INFO": {
                    "subject": f"कार्रवाई आवश्यक: दावा #{claim_id} के लिए अतिरिक्त दस्तावेज",
                    "body": f"प्रिय {claimant_name}, दावा #{claim_id} के निपटान में तेजी लाने के लिए कृपया निम्नलिखित दस्तावेज अपलोड करें: {', '.join(missing_docs) if missing_docs else 'स्पष्ट तस्वीरें'}।"
                },
                "APPROVED": {
                    "subject": f"दावा #{claim_id} स्वीकृत",
                    "body": f"प्रिय {claimant_name}, आपका दावा (#{claim_id}) स्वीकृत कर लिया गया है। भुगतान प्रक्रिया शुरू कर दी गई है।"
                },
                "REJECTED": {
                    "subject": f"दावा #{claim_id} के संबंध में अपडेट",
                    "body": f"प्रिय {claimant_name}, पॉलिसी शर्तों और साक्ष्यों की जांच के बाद, दावा #{claim_id} स्वीकृत नहीं किया जा सका।"
                },
                "MANUAL_REVIEW": {
                    "subject": f"दावा #{claim_id} विशेषज्ञ समीक्षा के लिए भेजा गया",
                    "body": f"प्रिय {claimant_name}, आपका दावा (#{claim_id}) विस्तृत सत्यापन के लिए वरिष्ठ अधिकारी को सौंपा गया है।"
                }
            },
            "kn": {
                "SUBMITTED": {
                    "subject": f"ವಿಮಾ ಹಕ್ಕು #{claim_id} ಸ್ವೀಕರಿಸಲಾಗಿದೆ - ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ",
                    "body": f"ಆತ್ಮೀಯ {claimant_name}, ನಿಮ್ಮ ವಿಮಾ ಹಕ್ಕು (#{claim_id}) ನಮಗೆ ತಲುಪಿದೆ. ನಮ್ಮ ಸ್ವಯಂಚಾಲಿತ ವ್ಯವಸ್ಥೆಯು ನಿಮ್ಮ ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸುತ್ತಿದೆ."
                },
                "REQUEST_INFO": {
                    "subject": f"ಕ್ರಮ ಅಗತ್ಯವಿದೆ: ಹಕ್ಕು #{claim_id} ಗಾಗಿ ಹೆಚ್ಚುವರಿ ದಾಖಲೆಗಳು",
                    "body": f"ಆತ್ಮೀಯ {claimant_name}, ದಯವಿಟ್ಟು ಈ ಮುಂದಿನ ದಾಖಲೆಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ: {', '.join(missing_docs) if missing_docs else 'ಘಟನೆಯ ಸ್ಪಷ್ಟ ಛಾಯಾಚಿತ್ರಗಳು'}."
                },
                "APPROVED": {
                    "subject": f"ವಿಮಾ ಹಕ್ಕು #{claim_id} ಅನುಮೋದಿಸಲಾಗಿದೆ",
                    "body": f"ಆತ್ಮೀಯ {claimant_name}, ಸಂತಸದ ಸುದ್ದಿ! ನಿಮ್ಮ ವಿಮಾ ಹಕ್ಕು (#{claim_id}) ಅನುಮೋದನೆಗೊಂಡಿದೆ. ಪರಿಹಾರ ಮೊತ್ತ ವರ್ಗಾವಣೆ ಪ್ರಕ್ರಿಯೆ ಆರಂಭಿಸಲಾಗಿದೆ."
                },
                "REJECTED": {
                    "subject": f"ವಿಮಾ ಹಕ್ಕು #{claim_id} ಕುರಿತು ಮಾಹಿತಿ",
                    "body": f"ಆತ್ಮೀಯ {claimant_name}, ಪಾಲಿಸಿ ನಿಯಮಗಳ ಪರಿಶೀಲನೆಯ ನಂತರ, ನಿಮ್ಮ ಹಕ್ಕು (#{claim_id}) ಅನುಮೋದಿಸಲಾಗಿಲ್ಲ."
                },
                "MANUAL_REVIEW": {
                    "subject": f"ವಿಮಾ ಹಕ್ಕು #{claim_id} ಪರಿಶೀಲಕರ ವಶದಲ್ಲಿದೆ",
                    "body": f"ಆತ್ಮೀಯ {claimant_name}, ನಿಮ್ಮ ಕ್ಲೈಮ್ ಅನ್ನು ಹಿರಿಯ ಪರಿಶೀಲನಾ ಅಧಿಕಾರಿಗೆ ವಹಿಸಲಾಗಿದೆ."
                }
            }
        }

        lang_data = templates.get(language, templates["en"])
        content = lang_data.get(status, lang_data["SUBMITTED"])
        return {
            "language": language,
            "subject": content["subject"],
            "message": content["body"]
        }
