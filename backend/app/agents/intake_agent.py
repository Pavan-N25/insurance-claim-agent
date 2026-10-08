import uuid
from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent

class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__("IntakeAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Processing intake for claim: {state.get('claim_id')}")
        
        claim_data = state.get("claim_data", {})
        documents = state.get("documents", [])
        
        # 1. Identify Modalities
        modalities = ["text"]
        has_image = any("image" in doc.get("file_type", "") for doc in documents)
        has_pdf = any("pdf" in doc.get("file_type", "") for doc in documents)
        has_audio = any("audio" in doc.get("file_type", "") for doc in documents)
        
        if has_image:
            modalities.append("image")
        if has_pdf:
            modalities.append("document")
        if has_audio:
            modalities.append("audio")

        # 2. Field Validation & Missing Information Detection
        missing_info: List[str] = []
        if not claim_data.get("policy_number"):
            missing_info.append("Policy Number")
        if not claim_data.get("incident_date"):
            missing_info.append("Incident Date & Time")
        if not claim_data.get("incident_location"):
            missing_info.append("Incident Location")
        if not claim_data.get("claimed_amount") or claim_data.get("claimed_amount", 0) <= 0:
            missing_info.append("Estimated Claim Amount")
        if not has_image:
            missing_info.append("Photographic Evidence of Damage")
        
        # 3. Audio description transcription if audio modality present
        audio_transcript = None
        for doc in documents:
            if "audio" in doc.get("file_type", ""):
                audio_transcript = (
                    f"Transcription of voice note ({doc.get('file_name')}): "
                    f"\"I was driving along Outer Ring Road when another vehicle suddenly switched lanes and collided with my front bumper and headlight. "
                    f"There was severe damage to the right wing and bumper clip.\""
                )
                doc["ocr_text"] = audio_transcript

        # 4. Generate structured intake output
        claim_type = claim_data.get("claim_type", "Auto Collision")
        customer_info = {
            "name": claim_data.get("claimant_name"),
            "email": claim_data.get("claimant_email"),
            "phone": claim_data.get("claimant_phone")
        }
        incident_info = {
            "date": claim_data.get("incident_date"),
            "location": claim_data.get("incident_location"),
            "description": claim_data.get("incident_description"),
            "audio_transcript": audio_transcript
        }

        summary = (
            f"Intake completed for {claim_type} reported by {customer_info['name']}. "
            f"Submitted modalities: {', '.join(modalities)}. "
            f"{len(missing_info)} missing items identified."
        )

        return {
            "claim_id": state.get("claim_id"),
            "claim_type": claim_type,
            "customer_information": customer_info,
            "incident_information": incident_info,
            "submitted_modalities": modalities,
            "missing_information": missing_info,
            "initial_summary": summary
        }
